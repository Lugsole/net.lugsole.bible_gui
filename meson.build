project('bible_gui',
          version: '0.1.3',
    meson_version: '>= 0.50.0',
  default_options: [ 'warning_level=2',
                   ],
)

i18n = import('i18n')
gnome = import('gnome')

version_date='2020-09-26'


if get_option('profile') == 'development'
  profile = '.Devel'
  name_suffix = ' Development'
  file_name_suffix = '-devel'
  path_suffix = '/devel'
  vcs_tag = run_command('git', 'rev-parse', '--short', 'HEAD').stdout().strip()
  if vcs_tag == ''
    version_suffix = '-devel'
  else
    version_suffix = '-@0@'.format (vcs_tag)
  endif
else
  profile = ''
  name_suffix = ''
  file_name_suffix = ''
  path_suffix = ''
  version_suffix = ''
endif

application_name_suffix = name_suffix
application_id = 'net.lugsole.bible_gui@0@'.format(profile)
application_path = '/net/lugsole/bible_gui@0@'.format(path_suffix)


subdir('data')
subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
