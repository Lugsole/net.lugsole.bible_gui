desktop_file = i18n.merge_file(
  input: 'net.lugsole.bible_gui.desktop.in',
  output: 'net.lugsole.bible_gui.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

conf = configuration_data()
conf.set('version', meson.project_version())
conf.set('version_date', version_date)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif
appstream_file = configure_file(
  input: 'net.lugsole.bible_gui.appdata.xml.in',
  output: 'net.lugsole.bible_gui.appdata.xml',
  po_dir: '../po',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metadata')
)

appstream_file = configure_file(
  input: 'net.lugsole.bible_gui.appdata.xml.in',
  output: 'net.lugsole.bible_gui.appdata.xml',
  po_dir: '../po',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

schema_src = 'net.lugsole.bible_gui.gschema.xml'
compiled = gnome.compile_schemas(build_by_default: true,
                                 depend_files: files(schema_src))

install_data(schema_src,
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
install_data('kjv.tsv',
  install_dir: pkgdatadir
)


subdir('icons')
