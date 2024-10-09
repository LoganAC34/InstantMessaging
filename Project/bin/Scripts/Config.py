import configparser

from Project.bin.Scripts.Global import GlobalVars


def get_user(user, num=1):
    """Gets attributes from config file, allowing 'user' to change when debug = True

        :param user: 'local' or 'remote'
        :param num: if user = 'remote', enter int
        :return: attribute value (string)
        """
    if user.lower() == 'local':
        user = 'LOCAL_USER'
    elif user.lower() == 'remote':
        if GlobalVars.debug:
            user = 'DEBUG_USER'
        else:
            user = f'REMOTE_USER_{num}'
    else:
        raise Exception("Not a recognized user type")

    return user


def create_template():
    config_template = configparser.ConfigParser()

    # Local user
    config_template['LOCAL_USER'] = {}
    config_template['LOCAL_USER']['alias'] = ""

    # First user and debug user
    cfg_headers = ['REMOTE_USER_1', 'DEBUG_USER']
    cfg_variables = ['alias', 'device_name', 'override']
    cfg_values = ['', '', 'False']
    for header in cfg_headers:
        config_template[header] = {}
        for variable, value in zip(cfg_variables, cfg_values):
            config_template[header][variable] = value

    # Write to config file
    with open(GlobalVars.cfgFile_path, 'x') as configfile:
        # noinspection PyTypeChecker
        config_template.write(configfile)


def get_user_info(att, user, num=1):
    """Gets attributes from config file, allowing 'user' to change when debug = True

    :param att: user attribute (see .cfg file)
    :param user: 'local' or 'remote'
    :param num: if user = 'remote', enter int
    :return: attribute value (string)
    """
    user = get_user(user, num)

    # Get Config values
    config = configparser.ConfigParser()
    config.read(GlobalVars.cfgFile_path)

    value = config[user][att]

    # Convert to bool if bool
    if value.lower() == 'false':
        value = False
    elif value.lower() == 'true':
        value = True

    return value


def set_user_info(att, val, user, num=1):
    """Sets attributes of config file, allowing 'user' to change when debug = True

        :param att: user attribute (see .cfg file)
        :param val: value of user attribute
        :param user: 'local' or 'remote'
        :param num: if user = 'remote', enter int
        :return: attribute value (string)
        """

    # Get Config values
    config = configparser.ConfigParser()
    config.read(GlobalVars.cfgFile_path)

    user = get_user(user, num)
    try:
        config.add_section(user)
        add_user()  # figure this out
    except configparser.DuplicateSectionError:
        pass
    config[user][att] = str(val)

    # Write to config file
    with open(GlobalVars.cfgFile_path, 'w') as configfile:  # save
        # noinspection PyTypeChecker
        config.write(configfile)


def get_user_count():
    """Returns how many remote users settings are set
        :return: int
    """
    # Get Config values
    config = configparser.ConfigParser()
    config.read(GlobalVars.cfgFile_path)

    n = 0
    while True:
        try:
            n += 1
            value = config[f'REMOTE_USER_{n}']
        except KeyError as e:
            # print(e)
            n -= 1
            return n


def add_user():
    user = get_user_count() + 1
    print(f"Adding user {user}")
    cfg_variables = ['alias', 'device_name', 'override']
    cfg_values = ['', '', False]

    config = configparser.ConfigParser()
    config.read(GlobalVars.cfgFile_path)
    header = f'REMOTE_USER_{user}'
    config[header] = {}
    for variable, value in zip(cfg_variables, cfg_values):
        config[header][variable] = ""

    # Write to config file
    with open(GlobalVars.cfgFile_path, 'w') as configfile:  # save
        # noinspection PyTypeChecker
        config.write(configfile)

    return user


def delete_user(user, num=1):
    """Gets attributes from config file, allowing 'user' to change when debug = True

        :param user: 'local' or 'remote'
        :param num: if user = 'remote', enter int
        :return: True if run successfully
        """

    config = configparser.ConfigParser()
    config.read(GlobalVars.cfgFile_path)

    n = 0
    while True:
        move_to = get_user(user, int(num) + n)
        n += 1
        move_from = get_user(user, int(num) + n)
        try:
            config[move_to] = config[move_from]
        except KeyError as e:
            config.remove_section(move_to)
            # print("No more users")
            # print(e)
            break

    # Write to config file
    with open(GlobalVars.cfgFile_path, 'w') as configfile:  # save
        # noinspection PyTypeChecker
        config.write(configfile)

    return True
