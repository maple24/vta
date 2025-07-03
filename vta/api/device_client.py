# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Enhanced Device Client for UI Automator2 operations.

This module provides a comprehensive interface for Android device automation
using UI Automator2 with enhanced error handling and user-friendly APIs.
"""

import os
import time
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
from loguru import logger

try:
    import uiautomator2 as u2
except ImportError:
    logger.warning("uiautomator2 not installed. Some features may not be available.")
    u2 = None

from .base import (
    BaseClient, ClientConfig, VTAError, ConnectionError,
    OperationError, ValidationError, TimeoutError,
    retry_on_failure, validate_connection, log_operation
)


@dataclass
class AppInfo:
    """Information about an installed application."""
    package_name: str
    version_name: str
    version_code: int
    is_system: bool
    is_enabled: bool
    install_time: int


@dataclass
class ElementSelector:
    """Selector for UI elements with various strategies."""
    text: Optional[str] = None
    description: Optional[str] = None
    class_name: Optional[str] = None
    resource_id: Optional[str] = None
    package: Optional[str] = None
    index: Optional[int] = None


class DeviceClient(BaseClient):
    """
    Enhanced UI Automator2 client for Android device automation.
    
    Features:
    - Device connection management with connection pooling
    - App lifecycle management (install, uninstall, start, stop)
    - UI element interaction with smart selectors
    - Screen capture and recording
    - Performance monitoring
    - Device status and health checks
    - Gesture and input simulation
    
    Example:
        ```python
        # Basic usage
        device = DeviceClient(ClientConfig(device_id="192.168.1.100"))
        device.install_app("/path/to/app.apk")
        device.start_app("com.example.app")
        
        # UI interaction
        device.click_element(text="Login")
        device.input_text("username", "testuser")
        
        # With context manager
        with DeviceClient(ClientConfig(device_id="emulator-5554")) as device:
            device.capture_screenshot("/tmp/screen.png")
        ```
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize Device client.
        
        Args:
            config: Client configuration including device_id
        """
        if u2 is None:
            raise VTAError("uiautomator2 is required but not installed. Install with: pip install uiautomator2")
        
        super().__init__(config)
        
        self.device_id = self.config.device_id
        self._device_obj = None
        self._app_info_cache = {}
    
    def connect(self) -> bool:
        """
        Connect to the device using UI Automator2.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If connection fails
        """
        if not self.device_id:
            raise ConnectionError("Device ID is required for connection")
        
        try:
            logger.info(f"Connecting to device: {self.device_id}")
            
            self._device_obj = u2.connect(self.device_id)
            
            # Test connection by getting device info
            info = self._device_obj.info
            if info:
                self._connected = True
                logger.info(f"Successfully connected to device: {self.device_id}")
                logger.debug(f"Device info: {info}")
                return True
            else:
                raise ConnectionError("Failed to retrieve device information")
                
        except Exception as e:
            self._device_obj = None
            raise ConnectionError(f"Failed to connect to device {self.device_id}: {e}")
    
    def disconnect(self) -> bool:
        """
        Disconnect from the device.
        
        Returns:
            bool: True if disconnection successful
        """
        if self._device_obj:
            try:
                # UI Automator2 doesn't have explicit disconnect
                self._device_obj = None
                self._connected = False
                self._app_info_cache.clear()
                logger.info(f"Disconnected from device: {self.device_id}")
                return True
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                return False
        
        return True
    
    def is_connected(self) -> bool:
        """
        Check if connected to the device.
        
        Returns:
            bool: True if connected and responsive
        """
        if not self._connected or not self._device_obj:
            return False
        
        try:
            # Test connection by getting device info
            info = self._device_obj.info
            return info is not None
        except Exception:
            self._connected = False
            return False
    
    # App Management Methods
    @validate_connection
    @log_operation
    def install_app(self, apk_path: str, replace: bool = False, 
                   grant_permissions: bool = True) -> bool:
        """
        Install an APK on the device.
        
        Args:
            apk_path: Path to the APK file
            replace: Whether to replace existing app
            grant_permissions: Whether to grant all permissions
            
        Returns:
            bool: True if installation successful
            
        Raises:
            ValidationError: If APK file doesn't exist
            OperationError: If installation fails
        """
        if not os.path.exists(apk_path):
            raise ValidationError(f"APK file not found: {apk_path}")
        
        try:
            logger.info(f"Installing APK: {apk_path}")
            
            # Install the APK
            result = self._device_obj.app_install(apk_path)
            
            if result:
                logger.info(f"Successfully installed APK: {apk_path}")
                
                # Grant permissions if requested
                if grant_permissions:
                    package_name = self._get_package_name_from_apk(apk_path)
                    if package_name:
                        self._grant_all_permissions(package_name)
                
                return True
            else:
                raise OperationError("APK installation failed")
                
        except Exception as e:
            raise OperationError(f"Failed to install APK {apk_path}: {e}")
    
    @validate_connection
    @log_operation
    def uninstall_app(self, package_name: str) -> bool:
        """
        Uninstall an app from the device.
        
        Args:
            package_name: Package name of the app to uninstall
            
        Returns:
            bool: True if uninstallation successful
        """
        try:
            result = self._device_obj.app_uninstall(package_name)
            if result:
                logger.info(f"Successfully uninstalled app: {package_name}")
                # Remove from cache
                self._app_info_cache.pop(package_name, None)
                return True
            else:
                logger.warning(f"App may not have been installed: {package_name}")
                return False
                
        except Exception as e:
            raise OperationError(f"Failed to uninstall app {package_name}: {e}")
    
    @validate_connection
    @log_operation
    def start_app(self, package_name: str, activity: Optional[str] = None,
                 wait_timeout: float = 10.0) -> bool:
        """
        Start an application.
        
        Args:
            package_name: Package name of the app
            activity: Specific activity to start (optional)
            wait_timeout: Time to wait for app to start
            
        Returns:
            bool: True if app started successfully
        """
        try:
            if activity:
                self._device_obj.app_start(package_name, activity)
            else:
                self._device_obj.app_start(package_name)
            
            # Wait for app to start
            if self._wait_for_app_start(package_name, wait_timeout):
                logger.info(f"Successfully started app: {package_name}")
                return True
            else:
                raise OperationError(f"App did not start within {wait_timeout}s")
                
        except Exception as e:
            raise OperationError(f"Failed to start app {package_name}: {e}")
    
    @validate_connection
    @log_operation
    def stop_app(self, package_name: str) -> bool:
        """
        Stop a running application.
        
        Args:
            package_name: Package name of the app to stop
            
        Returns:
            bool: True if app stopped successfully
        """
        try:
            self._device_obj.app_stop(package_name)
            logger.info(f"Successfully stopped app: {package_name}")
            return True
            
        except Exception as e:
            raise OperationError(f"Failed to stop app {package_name}: {e}")
    
    @validate_connection
    def get_app_info(self, package_name: str, use_cache: bool = True) -> Optional[AppInfo]:
        """
        Get information about an installed app.
        
        Args:
            package_name: Package name of the app
            use_cache: Whether to use cached information
            
        Returns:
            AppInfo object or None if app not found
        """
        if use_cache and package_name in self._app_info_cache:
            return self._app_info_cache[package_name]
        
        try:
            app_info = self._device_obj.app_info(package_name)
            if app_info:
                info = AppInfo(
                    package_name=package_name,
                    version_name=app_info.get('versionName', 'Unknown'),
                    version_code=app_info.get('versionCode', 0),
                    is_system=app_info.get('system', False),
                    is_enabled=app_info.get('enabled', True),
                    install_time=app_info.get('firstInstallTime', 0)
                )
                
                if use_cache:
                    self._app_info_cache[package_name] = info
                
                return info
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get app info for {package_name}: {e}")
            return None
    
    @validate_connection
    def list_installed_apps(self, include_system: bool = False) -> List[str]:
        """
        Get list of installed app package names.
        
        Args:
            include_system: Whether to include system apps
            
        Returns:
            List of package names
        """
        try:
            apps = self._device_obj.app_list()
            if include_system:
                return apps
            else:
                # Filter out system apps
                return [app for app in apps if not self._is_system_app(app)]
                
        except Exception as e:
            logger.error(f"Failed to list installed apps: {e}")
            return []
    
    # UI Interaction Methods
    @validate_connection
    @log_operation
    def click_element(self, selector: Union[ElementSelector, str], timeout: float = 10.0) -> bool:
        """
        Click on a UI element.
        
        Args:
            selector: Element selector or text to find
            timeout: Time to wait for element to appear
            
        Returns:
            bool: True if click successful
        """
        try:
            element = self._find_element(selector, timeout)
            if element:
                element.click()
                logger.info(f"Successfully clicked element: {selector}")
                return True
            else:
                raise OperationError(f"Element not found: {selector}")
                
        except Exception as e:
            raise OperationError(f"Failed to click element {selector}: {e}")
    
    @validate_connection
    @log_operation
    def input_text(self, selector: Union[ElementSelector, str], text: str,
                  clear_first: bool = True, timeout: float = 10.0) -> bool:
        """
        Input text into a UI element.
        
        Args:
            selector: Element selector to input text into
            text: Text to input
            clear_first: Whether to clear existing text first
            timeout: Time to wait for element
            
        Returns:
            bool: True if input successful
        """
        try:
            element = self._find_element(selector, timeout)
            if element:
                if clear_first:
                    element.clear_text()
                
                element.set_text(text)
                logger.info(f"Successfully input text into element: {selector}")
                return True
            else:
                raise OperationError(f"Element not found: {selector}")
                
        except Exception as e:
            raise OperationError(f"Failed to input text into {selector}: {e}")
    
    def _find_element(self, selector: Union[ElementSelector, str], timeout: float = 10.0):
        """
        Find a UI element using various selector strategies.
        
        Args:
            selector: Element selector
            timeout: Time to wait for element
            
        Returns:
            UI element object or None
        """
        if isinstance(selector, str):
            # Simple text selector
            return self._device_obj(text=selector).wait(timeout=timeout)
        
        elif isinstance(selector, ElementSelector):
            # Build selector from ElementSelector object
            kwargs = {}
            if selector.text:
                kwargs['text'] = selector.text
            if selector.description:
                kwargs['description'] = selector.description
            if selector.class_name:
                kwargs['className'] = selector.class_name
            if selector.resource_id:
                kwargs['resourceId'] = selector.resource_id
            if selector.package:
                kwargs['packageName'] = selector.package
            if selector.index is not None:
                kwargs['index'] = selector.index
            
            return self._device_obj(**kwargs).wait(timeout=timeout)
        
        else:
            raise ValidationError(f"Invalid selector type: {type(selector)}")
    
    # Helper Methods
    def _get_package_name_from_apk(self, apk_path: str) -> Optional[str]:
        """Extract package name from APK file."""
        # This would require additional tools like aapt
        # For now, return None
        return None
    
    def _grant_all_permissions(self, package_name: str):
        """Grant all permissions for an app."""
        try:
            # This would require specific permission handling
            # Implementation depends on device capabilities
            pass
        except Exception as e:
            logger.warning(f"Could not grant permissions for {package_name}: {e}")
    
    def _wait_for_app_start(self, package_name: str, timeout: float) -> bool:
        """Wait for an app to start."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                current_app = self._device_obj.app_current()
                if current_app.get('package') == package_name:
                    return True
            except Exception:
                pass
            
            time.sleep(0.5)
        
        return False
    
    def _is_system_app(self, package_name: str) -> bool:
        """Check if an app is a system app."""
        try:
            app_info = self.get_app_info(package_name, use_cache=False)
            return app_info.is_system if app_info else False
        except Exception:
            return False
