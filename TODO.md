# Refactor

1. add strong type hints
2. use pydantic model
3. add unit tests

## Workflow

1. add pre-commit

## ways to start an android application

```sh
adb shell am start -n <package_name>/<activity_name>
#  If you're unsure about the activity name, you can use the application package name alone, and Android will attempt to start the default/main activity of the application.
adb shell am start -n com.example.myapp/.MainActivity
```

### find package name

```sh
adb shell pm list packages
```

### find activity name

```sh
adb shell cmd package resolve-activity --brief <package_name>
```
