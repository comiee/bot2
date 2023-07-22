from alicebot import Bot
from alicebot.utils import get_classes_from_module
from alicebot.log import error_or_exception, logger
from alicebot.exceptions import LoadModuleError
import alicebot.utils
import importlib
import os
import alicebot.bot

__all__ = ['run_bot']


# 解决alicebot加载两次plugins目录的问题，同时解决加载插件时报错太难看的问题，强制要求加载所有插件
def repair_get_classes_from_module_name():
    def _get_classes_from_module_name(name, super_class):
        importlib.invalidate_caches()
        module = importlib.import_module(name)
        return [(x, module) for x in get_classes_from_module(module, super_class)]

    alicebot.utils.get_classes_from_module_name = _get_classes_from_module_name
    importlib.reload(importlib.import_module('alicebot.bot'))


# 解决plugin优先级只能使用int不能使用int的子类的问题
def repair_load_plugin_class():
    def _load_plugin_class(self, plugin_class, plugin_load_type, plugin_file_path):
        """加载插件类。"""
        priority = getattr(plugin_class, "priority", None)
        if isinstance(priority, int) and priority >= 0:
            for _plugin in self.plugins:
                if _plugin.__name__ == plugin_class.__name__:
                    logger.warning(
                        f'Already have a same name plugin "{_plugin.__name__}"'
                    )
            plugin_class.__plugin_load_type__ = plugin_load_type
            plugin_class.__plugin_file_path__ = plugin_file_path
            self.plugins_priority_dict[priority].append(plugin_class)
            logger.info(
                f'Succeeded to load plugin "{plugin_class.__name__}" '
                f'from class "{plugin_class!r}"'
            )
        else:
            error_or_exception(
                f'Load plugin from class "{plugin_class!r}" failed:',
                LoadModuleError(
                    f'Plugin priority incorrect in the class "{plugin_class!r}"'
                ),
                self.config.bot.log.verbose_exception,
            )

    Bot._load_plugin_class = _load_plugin_class


def repair_alice():
    repair_get_classes_from_module_name()
    repair_load_plugin_class()


def run_bot():
    repair_alice()
    os.chdir(os.path.dirname(__file__))
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    run_bot()
