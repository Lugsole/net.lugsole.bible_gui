pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'bible')

gnome.compile_resources('bible',
  'bible.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('ESPEAK', find_program('espeak').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'bible.in',
  output: 'bible',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

configure_file(
  input: 'config.py.in',
  output: 'config.py',
  configuration: conf,
  install: true,
  install_dir: moduledir
)

bible_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'tts.py',
  'Bible_Parser.py',
  'Bible_Parser_Base.py',
  'Bible_Parser_sqlite.py',
  'Bible_Parser_spb.py',
  'Bible_Parser_xml.py',
  'Bible.py',
  'Audio_Player.py',
  'Bible_Parser_tsv.py',
  'settings.py'
]

libhandy_dep = dependency('libhandy-1',
  version: '>=0.84.0'
  )


install_data(bible_sources, install_dir: moduledir)
