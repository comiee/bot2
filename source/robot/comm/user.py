class User(int):
    def is_super_user(self):
        return self == 1440667228  # TODO 后续改成toml配置文件，并添加手动重新加载功能
