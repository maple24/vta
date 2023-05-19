"""Lightweight library for flexray xml database parser
"""
__all__ = [
    "FlexrayDatabase",
    "SignalInfoPo",
    "PersistentFlexrayDatabase",
    "FlexrayDatabaseException",
]
__author__ = "usy2wx"

from os.path import basename
from typing import Optional
from xml.etree import ElementTree

XML_NAMESPACE = {  # XML namespaces
    "can": "http://www.asam.net/xml/fbx/can",
    "flexray": "http://www.asam.net/xml/fbx/flexray",
    "fx": "http://www.asam.net/xml/fbx",
    "ho": "http://www.asam.net/xml",
    "lin": "http://www.asam.net/xml/fbx/lin",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def _logger(*value: object) -> None:
    print(f"[{basename(__file__)}] ", end="")
    print(*value)


class FlexrayDatabaseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FlexrayDatabase:
    """Flexray Database parser based on ElementTree & XPath"""

    def __init__(self, database: str) -> None:
        """__init__, initialization of database of flexray

        :param str database: Flexray database XML file path
        :raises FlexrayDatabaseException: Failed to parse XML
        """
        _logger("Start to initialize FlexrayDatabase")
        self.tree = ElementTree.parse(database)
        self.root = self.tree.getroot()

        # useful sub node initialization
        self.channels_element = self.root.find(
            path="fx:ELEMENTS/fx:CHANNELS", namespaces=XML_NAMESPACE
        )
        if self.channels_element is None:
            _logger("Failed to get fx:CHANNELS")
            raise FlexrayDatabaseException("Failed to get fx:CHANNELS")

        self.pdus_element = self.root.find(
            path="fx:ELEMENTS/fx:PDUS", namespaces=XML_NAMESPACE
        )
        if self.pdus_element is None:
            _logger("Failed to get fx:PDUS node")
            raise FlexrayDatabaseException("Failed to get fx:PDUS node")

        self.frames_element = self.root.find(
            path="fx:ELEMENTS/fx:FRAMES", namespaces=XML_NAMESPACE
        )
        if self.frames_element is None:
            _logger("Failed to get fx:FRAMES node")
            raise FlexrayDatabaseException("Failed to get fx:FRAMES node")

        self.signals_element = self.root.find(
            path="fx:ELEMENTS/fx:SIGNALS", namespaces=XML_NAMESPACE
        )
        if self.signals_element is None:
            _logger("Failed to get fx:SIGNAL node")
            raise FlexrayDatabaseException("Failed to get fx:SIGNAL node")

        self.codings_element = self.root.find(
            path="fx:PROCESSING-INFORMATION/fx:CODINGS", namespaces=XML_NAMESPACE
        )
        if self.codings_element is None:
            _logger("Failed to get fx:CODINGS node")
            raise FlexrayDatabaseException("Failed to get fx:CODINGS node")

        _logger("Succeeded to initialize FlexrayDatabase")

    def get_slot_id_by_pdu_name(self, pdu_name: str) -> int:
        """Get slot ID of Flexray DPU name

        :param str pdu_name: PDU name to get, contains "Ipdu" in it
        :return int: Slot ID if succeeded, other wise -1
        """
        frame_trigger_element = self._get_frame_triggering_element_by_pdu_name(pdu_name)
        if frame_trigger_element is None:
            return -1

        slot_id_element = frame_trigger_element.find(
            path=".//*/fx:SLOT-ID", namespaces=XML_NAMESPACE
        )
        if slot_id_element is None or slot_id_element.text is None:
            _logger(f"Failed to get slot ID by PDU name: {pdu_name}")
            return -1

        return int(slot_id_element.text)

    def get_base_cycle_by_pdu_name(self, pdu_name: str) -> int:
        """Get base cycle of Flexray DPU name

        :param str pdu_name: PDU name to get, contains "Ipdu" in it
        :return int: Base cycle if succeeded, other wise -1
        """
        frame_trigger_element = self._get_frame_triggering_element_by_pdu_name(pdu_name)
        if frame_trigger_element is None:
            return -1

        base_cycle_element = frame_trigger_element.find(
            path=".//*/fx:BASE-CYCLE", namespaces=XML_NAMESPACE
        )
        if base_cycle_element is None or base_cycle_element.text is None:
            _logger(f"Failed to get slot ID by PDU name: {pdu_name}")
            return -1

        return int(base_cycle_element.text)

    def get_cycle_repetition_by_pdu_name(self, pdu_name: str) -> int:
        """Get cycle repetition of Flexray DPU name

        :param str pdu_name: PDU name to get, contains "Ipdu" in it
        :return int: Cycle repetition if succeeded, other wise -1
        """
        frame_trigger_element = self._get_frame_triggering_element_by_pdu_name(pdu_name)
        if frame_trigger_element is None:
            return -1

        cycle_repetition_element = frame_trigger_element.find(
            path=".//*/fx:CYCLE-REPETITION", namespaces=XML_NAMESPACE
        )
        if cycle_repetition_element is None or cycle_repetition_element.text is None:
            _logger(f"Failed to get slot ID by PDU name: {pdu_name}")
            return -1

        return int(cycle_repetition_element.text)

    def _get_frame_triggering_element_by_pdu_name(
        self, pdu_name: str
    ) -> Optional[ElementTree.Element]:
        pdu_id = self._get_pdu_id_by_name(pdu_name)
        if not pdu_id:
            return None

        frame_id = self._get_frame_id_by_pdu_id(pdu_id)
        if not frame_id:
            return None

        return self._get_frame_triggering_element_by_frame_id(frame_id)

    def get_bit_position_by_signal_name(self, signal_name: str) -> int:
        """Get bit position (in PDU) of Flexray signal name

        :param str signal_name: Signal name to get
        :return int: Bit position if succeeded, other wise -1
        """
        signal_id = self._get_signal_id_by_name(signal_name)
        assert self.pdus_element
        signal_instance_element = self.pdus_element.find(
            path=f'.//*[@ID-REF="{signal_id}"]/..', namespaces=XML_NAMESPACE
        )
        if signal_instance_element is None:
            _logger(f"Failed to get signal instance node by signal ID: {signal_id}")
            return -1

        bit_position_element = signal_instance_element.find(
            path=".//fx:BIT-POSITION", namespaces=XML_NAMESPACE
        )
        if bit_position_element is None or bit_position_element.text is None:
            _logger(f"Failed to get bit position by signal name: {signal_name}")
            return -1

        return int(bit_position_element.text)

    def get_bit_length_by_signal_name(self, signal_name: str) -> int:
        """Get bit length of Flexray signal name

        :param str signal_name: Signal name to get
        :return int: Bit length if succeeded, other wise -1
        """
        signal_element = self._get_signal_element_by_name(signal_name)
        if signal_element is None:
            _logger(f"Failed to get signal element by signal name {signal_name}")
            return -1

        coding_ref_element = signal_element.find(
            path="./fx:CODING-REF", namespaces=XML_NAMESPACE
        )
        if coding_ref_element is None:
            _logger(
                f"Failed to get coding reference element by signal name: {signal_name}"
            )
            return -1

        coding_ref_id = coding_ref_element.attrib.get("ID-REF")
        if coding_ref_id is None or not coding_ref_id:
            _logger(f"Failed to get coding reference ID by signal name: {signal_name}")
            return -1

        coding_element = self._get_coding_element_by_ref_id(coding_ref_id)
        if coding_element is None:
            _logger(f"Failed to get coding node by signal name: {signal_name}")
            return -1

        bit_length_element = coding_element.find(
            path=".//*/ho:BIT-LENGTH", namespaces=XML_NAMESPACE
        )
        if bit_length_element is None or bit_length_element.text is None:
            _logger(f"Failed to get bit length node by signal name: {signal_name}")
            return -1

        return int(bit_length_element.text)

    #
    # <fx:PDU ID="ID_0e198869-4686-4eb1-a772-e76662ca2e62">
    #    <ho:SHORT-NAME>CEMBackBoneSignalIpdu02</ho:SHORT-NAME>
    #    <fx:BYTE-LENGTH>32</fx:BYTE-LENGTH>
    #     <fx:PDU-TYPE>APPLICATION</fx:PDU-TYPE>
    #    <fx:SIGNAL-INSTANCES>
    #      <fx:SIGNAL-INSTANCE ID="d3a905e2-a82c-3f79-9a2c-bac77aebb286">
    #        <fx:BIT-POSITION>64</fx:BIT-POSITION>
    #        <fx:IS-HIGH-LOW-BYTE-ORDER>true</fx:IS-HIGH-LOW-BYTE-ORDER>
    #        <fx:SIGNAL-REF ID-REF="IDDKDataFromCEM_UB"/>
    def get_pdu_name_by_signal_name(self, signal_name: str) -> str:
        """Get PDU name by signal name

        :param str signal_name: Signal short name
        :return str: PDU short name
        """
        signal_id = self._get_signal_id_by_name(signal_name)
        if not signal_id:
            _logger(f"Failed to get signal ID by name: {signal_name}")
            return ""

        assert self.pdus_element
        pdu_element = self.pdus_element.find(
            path=f'.//*[@ID-REF="{signal_id}"]/../../..', namespaces=XML_NAMESPACE
        )
        if pdu_element is None:
            _logger(f"Failed to get PDU element by signal ref ID: {signal_id}")
            return ""

        short_name_element = pdu_element.find(
            path="./ho:SHORT-NAME", namespaces=XML_NAMESPACE
        )
        if short_name_element is None or short_name_element.text is None:
            _logger(f"Failed to get PDU short name by signal ref ID: {signal_id}")
            return ""

        return short_name_element.text

    #
    # <fx:SIGNALS>
    #   <fx:SIGNAL ID="IDVehModMngtGlbSafe1_UB">
    #     <ho:SHORT-NAME>VehModMngtGlbSafe1_UB</ho:SHORT-NAME>
    #     <fx:CODING-REF ID-REF="Coding1"/>
    #     <fx:SIGNAL-TYPE>
    #       <fx:TYPE>OTHER</fx:TYPE>
    #       <fx:METHOD>Signal-group-update-bit</fx:METHOD>
    #       <fx:ATTRIBUTES>
    #         <fx:ATTRIBUTE>VehModMngtGlbSafe1</fx:ATTRIBUTE>
    #       </fx:ATTRIBUTES>
    #     </fx:SIGNAL-TYPE>
    #   </fx:SIGNAL>
    #
    #   <fx:SIGNAL ID="OtherID">
    #     <ho:SHORT-NAME>OtherSignalName</ho:SHORT-NAME>
    #     ...
    #   </fx:SIGNAL>
    #
    # <fx:SIGNALS>
    def _get_signal_element_by_name(self, name: str) -> Optional[ElementTree.Element]:
        assert self.signals_element
        signal_element = self.signals_element.find(
            path=f'.//*/[.="{name}"]/..', namespaces=XML_NAMESPACE
        )
        if signal_element is None:
            _logger(f"Signal short name: {name} not found in xml")

        return signal_element

    def _get_signal_id_by_name(self, name: str) -> str:
        signal_element = self._get_signal_element_by_name(name)
        if signal_element is None:
            _logger("Failed to get signal node in xml")
            return ""

        signal_id = signal_element.attrib.get("ID")
        if signal_id is None or not signal_id:
            _logger(f"Failed to get signal ID of {name}")
            return ""

        return signal_id

    #
    # <fx:PDUS>
    # <fx:PDU ID="ID_0e198869-4686-4eb1-a772-e76662ca2e62">
    #   <ho:SHORT-NAME>CEMBackBoneSignalIpdu02</ho:SHORT-NAME>
    #   <fx:BYTE-LENGTH>32</fx:BYTE-LENGTH>
    #   <fx:PDU-TYPE>APPLICATION</fx:PDU-TYPE>
    #   <fx:SIGNAL-INSTANCES>
    #     <fx:SIGNAL-INSTANCE ID="d3a905e2-a82c-3f79-9a2c-bac77aebb286">
    #       <fx:BIT-POSITION>64</fx:BIT-POSITION>
    #       <fx:IS-HIGH-LOW-BYTE-ORDER>true</fx:IS-HIGH-LOW-BYTE-ORDER>
    #       <fx:SIGNAL-REF ID-REF="IDDKDataFromCEM_UB"/>
    #     </fx:SIGNAL-INSTANCE>
    #
    #     <fx:SIGNAL-INSTANCE ID="ID_4aae9c8b-6d5b-3ee5-9f7b-11c770c8278a">
    #       <fx:BIT-POSITION>175</fx:BIT-POSITION>
    #       ...
    def _get_pdu_element_by_name(self, name: str) -> Optional[ElementTree.Element]:
        assert self.pdus_element
        pdu_element = self.pdus_element.find(
            path=f'.//*/[.="{name}"]/..', namespaces=XML_NAMESPACE
        )
        if pdu_element is None:
            _logger(f"PDU short name: {name} not found in xml")

        return pdu_element

    def _get_pdu_id_by_name(self, name: str) -> str:
        pdu_element = self._get_pdu_element_by_name(name)
        if pdu_element is None:
            _logger("Failed to get PDU node in xml")
            return ""

        pdu_id = pdu_element.attrib.get("ID", "")
        if not pdu_id:
            _logger(f"Failed to get PDU ID of {name}")

        return pdu_id

    #
    #
    # <fx:FRAMES>
    #  <fx:FRAME ID="ID_1dc439f8-da53-4b09-ad09-af58f65c9a54">
    #    <ho:SHORT-NAME>AdcuBackBoneFr01</ho:SHORT-NAME>
    #    <fx:BYTE-LENGTH>32</fx:BYTE-LENGTH>
    #    <fx:FRAME-TYPE>APPLICATION</fx:FRAME-TYPE>
    #    <fx:PDU-INSTANCES>
    #      <fx:PDU-INSTANCE ID="ID_1dc439f8-da53-4b09-ad09 ... >
    #        <fx:PDU-REF ID-REF="ID_0a8bc654-542e-481a-84c5-51a2e37d8377"/>
    #        <fx:BIT-POSITION>0</fx:BIT-POSITION>
    #        <fx:IS-HIGH-LOW-BYTE-ORDER>false</fx:IS-HIGH-LOW-BYTE-ORDER>
    #      </fx:PDU-INSTANCE>
    #    </fx:PDU-INSTANCES>
    #  </fx:FRAME>
    #
    #  <fx:FRAME ID="ID_52521796-31ee-4d1e-8719-7b4c950f3fee">
    #    <ho:SHORT-NAME>AdcuBackBoneFr02</ho:SHORT-NAME>
    #    ...
    def _get_frame_element_by_pdu_id(
        self, pdu_id: str
    ) -> Optional[ElementTree.Element]:
        assert self.frames_element
        frame_element = self.frames_element.find(
            path=f'.//*[@ID-REF="{pdu_id}"]/../../..', namespaces=XML_NAMESPACE
        )
        if frame_element is None:
            _logger(f"Frame node not found by pdu id: {pdu_id}")

        return frame_element

    def _get_frame_id_by_pdu_id(self, pdu_id: str) -> str:
        frame_element = self._get_frame_element_by_pdu_id(pdu_id)
        if frame_element is None:
            _logger(f"Failed to get frame node by PDU id: {pdu_id}")
            return ""

        frame_id = frame_element.get("ID", "")
        if not frame_id:
            _logger(f"Failed to get frame by PUD id: {pdu_id}")

        return frame_id

    #
    # <fx:FRAME-TRIGGERING ID="IDftr_b634a90d-fadd-3846-bd89-3be8320a729c_A">
    #   <fx:TIMINGS>
    #     <fx:ABSOLUTELY-SCHEDULED-TIMING>
    #       <fx:SLOT-ID>36</fx:SLOT-ID>
    #       <fx:BASE-CYCLE>0</fx:BASE-CYCLE>
    #       <fx:CYCLE-REPETITION>1</fx:CYCLE-REPETITION>
    #     </fx:ABSOLUTELY-SCHEDULED-TIMING>
    #   </fx:TIMINGS>
    #   <fx:FRAME-REF ID-REF="ID_744b7a52-30ea-4ec9-be86-052d613a2737"/>
    # </fx:FRAME-TRIGGERING>
    def _get_frame_triggering_element_by_frame_id(
        self, frame_id: str
    ) -> Optional[ElementTree.Element]:
        assert self.channels_element
        frame_triggering_element = self.channels_element.find(
            path=f'.//*[@ID-REF="{frame_id}"]/..'
        )
        if frame_triggering_element is None:
            _logger(f"Failed to get frame triggering node by frame ID: {frame_id}")

        return frame_triggering_element

    #
    # <fx:CODINGS>
    #  <fx:CODING ID="CM-ID_AF8B51932A24413F20819538EA86D704_1">
    #    <ho:SHORT-NAME>A32_1</ho:SHORT-NAME>
    #    <ho:CODED-TYPE ho:BASE-DATA-TYPE="A_INT8" ... >
    #      <ho:BIT-LENGTH>8</ho:BIT-LENGTH>
    def _get_coding_element_by_ref_id(
        self, ref_id: str
    ) -> Optional[ElementTree.Element]:
        assert self.codings_element
        coding_element = self.codings_element.find(
            path=f'.//*/[@ID="{ref_id}"]', namespaces=XML_NAMESPACE
        )
        if coding_element is None:
            _logger(f"Failed to get coding node by reference ID: {ref_id}")

        return coding_element

    @NotImplementedError
    def get_slot_id_by_frame_name(self):
        pass


class SignalInfoPo:
    """Persistent Object of one Flexray signal"""

    def __init__(
        self,
        signal_name: str,
        slot_id: int,
        base_cycle: int,
        cycle_repetition: int,
        bit_position: int,
        bit_length: int,
    ) -> None:
        self.signal_name: str = signal_name
        self.slot_id = slot_id
        self.base_cycle = base_cycle
        self.cycle_repetition = cycle_repetition
        self.bit_position = bit_position
        self.bit_length = bit_length

    def __str__(self) -> str:
        output = [f"[{self.signal_name}]"]
        output.append(f"slot: {self.slot_id}")
        output.append(f"base: {self.base_cycle}")
        output.append(f"rep: {self.cycle_repetition}")
        output.append(f"pos: {self.bit_position}")
        output.append(f"len: {self.bit_length}")

        return " ".join(output)


class PersistentFlexrayDatabase(FlexrayDatabase):
    """Flexray Database with cache"""

    def __init__(self, database: str) -> None:
        super().__init__(database)
        self.cache: dict[str, SignalInfoPo] = {}

    def get_signal_info_po_by_name(self, signal_name: str) -> Optional[SignalInfoPo]:
        """Get instance of SignalInfoPo by signal name

        :param str signal_name: Signal short name
        """
        if signal_name in self.cache:
            return self.cache[signal_name]

        pdu_name = self.get_pdu_name_by_signal_name(signal_name)
        if not pdu_name:
            return None

        slot_id = self.get_slot_id_by_pdu_name(pdu_name)
        if slot_id == -1:
            return None

        base_cycle = self.get_base_cycle_by_pdu_name(pdu_name)
        if base_cycle == -1:
            return None

        cycle_repetition = self.get_cycle_repetition_by_pdu_name(pdu_name)
        if cycle_repetition == -1:
            return None

        bit_position = self.get_bit_position_by_signal_name(signal_name)
        if bit_position == -1:
            return None

        bit_length = self.get_bit_length_by_signal_name(signal_name)
        if bit_length == -1:
            return None

        signal_info_po = SignalInfoPo(
            signal_name=signal_name,
            slot_id=slot_id,
            base_cycle=base_cycle,
            cycle_repetition=cycle_repetition,
            bit_position=bit_position,
            bit_length=bit_length,
        )
        self.cache[signal_name] = signal_info_po
        _logger(f"PersistentFlexrayDatabase Updated: {signal_info_po}")
        return signal_info_po


def high_level_test(signal_string: str):
    db = FlexrayDatabase("SDB22200_G426_ICE_High_BackboneFR_220706.xml")

    if signal_string.startswith("user_"):
        # Compatible for SBox syntax
        signal_string = signal_string[5:]

    tokens = signal_string.split(",")
    if len(tokens) != 3:
        print("Invalid command")
        return

    #
    # user_CEMBackBoneSignalIpdu02,VehModMngtGlbSafe1_UB,1
    # CEMBackBoneSignalIpdu02,VehModMngtGlbSafe1_UB,1
    pdu_name, signal_name, signal_value = [s.strip() for s in tokens]
    print(f"{pdu_name}.{signal_name} := {signal_value}")

    slot_id = db.get_slot_id_by_pdu_name(pdu_name)
    base_cycle = db.get_base_cycle_by_pdu_name(pdu_name)
    bit_position = db.get_bit_position_by_signal_name(signal_name)
    bit_length = db.get_bit_length_by_signal_name(signal_name)
    print(f"slot id: {slot_id}, base_cycle: {base_cycle}")
    print(f"bit position: {bit_position}, bit length: {bit_length}")

    del db
    db = PersistentFlexrayDatabase("SDB22200_G426_ICE_High_BackboneFR_220706.xml")
    print(db.get_signal_info_po_by_name(signal_name))
    # To test cache works fine
    print(db.get_signal_info_po_by_name(signal_name))


if __name__ == "__main__":
    high_level_test("user_CEMBackBoneSignalIpdu02,VehModMngtGlbSafe1_UB,1")
    high_level_test("user_CEMBackBoneSignalIpdu02,VehModMngtGlbSafe1UsgModSts,11")
