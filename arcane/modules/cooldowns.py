import time


class CommandCooldown:
    def __init__(self):
        self.cooldowns = {}

    def can_use_command(self, command, cooldown_duration):
        current_time = time.time()
        last_used_time = self.cooldowns.get(command, 0)

        if current_time - last_used_time < cooldown_duration:
            return False
        return True

    def update_command_cooldown(self, command):
        self.cooldowns[command] = time.time()


command_cooldown_manager = CommandCooldown()
