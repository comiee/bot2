from public.log import main_logger
import pkgutil


def load_module(path):
    """加载路径下的所有py文件，不包括__init__.py和子包"""
    dirs = [path]
    pkgutil.extend_path(dirs, path)
    for loader, module_name, is_pkg in pkgutil.iter_modules(dirs):
        if not is_pkg:
            main_logger.info(f'正在从{loader.path}加载{module_name}')  # 这个阶段在启动前，报错直接打印，不用记到日志文件里
            loader.find_module(module_name).load_module()
