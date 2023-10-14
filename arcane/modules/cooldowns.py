import time


class CommandCooldown:
    def __init__(self):
        self.cooldowns = {}

    def can_use_command(self, channel, command, cooldown_duration):
        current_time = time.time()
        channel = self.cooldowns.get(channel, {})

        if channel:
            last_used_time = channel.get(command, 0)

            if current_time - last_used_time < cooldown_duration:
                return False
        return True

    def update_command_cooldown(self, channel, command):
        self.cooldowns[channel] = {}
        self.cooldowns[channel][command] = time.time()


command_cooldown_manager = CommandCooldown()
