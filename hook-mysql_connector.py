from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('mysql.connector')

hiddenimports = collect_submodules('mysql.connector')
hiddenimports.extend([
    'mysql.connector.plugins.mysql_native_password',
    'mysql.connector.plugins.caching_sha2_password',
    'mysql.connector.plugins.mysql_clear_password',
])
