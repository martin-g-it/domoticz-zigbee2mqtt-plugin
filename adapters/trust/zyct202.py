from adapters.adapter_with_battery import AdapterWithBattery
from devices.switch.selector_switch import SelectorSwitch


class ZYCT202(AdapterWithBattery):
    def __init__(self, devices):
        super().__init__(devices)

        device_count = 6

        for device_index in range(1, device_count + 1):
            self.devices.append(self.create_device(devices, device_index))

    def create_device(self, devices, index):
        device = SelectorSwitch(devices, 'dev' + str(index), 'action', ' (Device ' + str(index) + ')')
        device.add_level('Off', None)
        device.add_level('On', 'on')
        device.add_level('Up', 'up-press')
        device.add_level('Down', 'down-press')
        device.add_level('Stop', 'stop')
        device.set_selector_style(SelectorSwitch.SELECTOR_TYPE_BUTTONS)
        device.disable_value_check_on_update()

        return device

    def handle_command(self, alias, device, command, level, color):
        device_data = self._get_legacy_device_data()
        device = self.get_device_by_alias(alias)
        device.handle_command(device_data, command, level, color)

    def handle_mqtt_message(self, message):
        if 'action' not in message.raw or 'action_group' not in message.raw:
            return

        device_data = self._get_legacy_device_data()
        converted_message = self.convert_message(message)
        device_index = message.raw['action_group']

        # Convert action_group to device index (below some known ranges)
        if ( device_index >= 145 and device_index <= 150 ):
            device_index = device_index - 144
        elif ( device_index >= 23118 and device_index <= 23123 ):
            device_index = device_index - 23117
        elif ( device_index >= 24837 and device_index <= 24842 ):
            device_index = device_index - 24836
        elif ( device_index >= 23484 and device_index <= 23489 ):
            device_index = device_index - 23483

        device = self.get_device_by_alias('dev' + str(device_index))
        device.handle_message(device_data, converted_message)

        self.update_battery_status(device_data, converted_message)
        self.update_link_quality(device_data, converted_message)
