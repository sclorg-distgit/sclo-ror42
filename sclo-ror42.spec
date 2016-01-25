%global scl_name_prefix sclo-
%global scl_name_base ror
%global scl_name_version 42

%global scl %{scl_name_prefix}%{scl_name_base}%{scl_name_version}

# Fallback to rh-ruby22. rh-ruby22-scldevel is probably not available in
# the buildroot.
%{!?scl_ruby:%global scl_ruby rh-ruby22}
%{!?scl_prefix_ruby:%global scl_prefix_ruby %{scl_ruby}-}

# Do not produce empty debuginfo package.
%global debug_package %{nil}

# Support SCL over NFS.
%global nfsmountable 1

%{!?install_scl: %global install_scl 1}

%scl_package %scl

Summary: Package that installs %scl
Name: %scl_name
Version: 3.0
Release: 2%{?dist}
License: GPLv2+
Source0: README
Source1: LICENSE
%if 0%{?install_scl}
Requires: %{scl_prefix}rubygem-therubyracer
Requires: %{scl_prefix}rubygem-sqlite3
Requires: %{scl_prefix}rubygem-rails
Requires: %{scl_prefix}rubygem-sass-rails
Requires: %{scl_prefix}rubygem-coffee-rails
Requires: %{scl_prefix}rubygem-jquery-rails
Requires: %{scl_prefix}rubygem-sdoc
Requires: %{scl_prefix}rubygem-turbolinks
Requires: %{scl_prefix}rubygem-bcrypt
Requires: %{scl_prefix}rubygem-uglifier
Requires: %{scl_prefix}rubygem-jbuilder
Requires: %{scl_prefix}rubygem-spring
%endif
BuildRequires: help2man
BuildRequires: scl-utils-build
BuildRequires: %{scl_prefix_ruby}scldevel
BuildRequires: %{scl_prefix_ruby}rubygems-devel

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils
# enable scriptlet depends on ruby executable.
Requires: %{scl_prefix_ruby}ruby

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build
Requires: %{scl_runtime}
Requires: %{scl_prefix_ruby}scldevel
Requires: v8314-scldevel

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl
Provides: scldevel(%{scl_name_base})

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

# Expand macros used in README file.
cat > README << EOF
%{expand:%(cat %{SOURCE0})}
EOF

cp %{SOURCE1} .

%build
# Generate a helper script that will be used by help2man.
cat > h2m_help << 'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_help

# Generate the man page from include.h2m and ./h2m_help --help output.
help2man -N --section 7 ./h2m_help -o %{scl_name}.7

%install
%scl_install

cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
export GEM_PATH=\${GEM_PATH:=%{gem_dir}:\`scl enable %{scl_ruby} -- ruby -e "print Gem.path.join(':')"\`}

. scl_source enable %{scl_ruby}
EOF

cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# Install generated man page.
mkdir -p %{buildroot}%{_mandir}/man7/
install -p -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/

scl enable %{scl_ruby} - << \EOF
set -e

# Fake sclo-ror42 SCL environment.
# TODO: Is there a way how to leverage the enable scriptlet created above?
GEM_PATH=%{gem_dir}:`ruby -e "print Gem.path.join(':')"` \
X_SCLS=%{scl} \
ruby -rfileutils > rubygems_filesystem.list << \EOR
  # Create RubyGems filesystem.
  Gem.ensure_gem_subdirectories '%{buildroot}%{gem_dir}'
  FileUtils.mkdir_p File.join '%{buildroot}', Gem.default_ext_dir_for('%{gem_dir}')

  # Output the relevant directories.
  Gem.default_dirs['%{scl}_system'.to_sym].each { |k, p| puts p }
EOR
EOF

%files

%files runtime -f rubygems_filesystem.list
%doc README LICENSE
%scl_files
# Own the manual directories (rhbz#1080036, rhbz#1072319).
%dir %{_mandir}/man1
%dir %{_mandir}/man5
%dir %{_mandir}/man7
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel


%changelog
* Mon Jan 25 2016 Dominic Cleal <dcleal@redhat.com> 3.0-2
- Depend on v8314-scldevel from -build for therubyracer

* Fri Dec 11 2015 Dominic Cleal <dcleal@redhat.com> 3.0-1
- Update metapackage from rh-ror41 to sclo-ror42

* Tue Mar 31 2015 Vít Ondruch <vondruch@redhat.com> - 2.0-6
- A few spelling corrections in README and man pages.
  Resolves: rhbz#1206175

* Tue Mar 10 2015 Vít Ondruch <vondruch@redhat.com> - 2.0-5
- Rebuild to remove 'scls' direcotories created by scl-utils.
  Resolves: rhbz#1200060

* Wed Feb 04 2015 Vít Ondruch <vondruch@redhat.com> - 2.0-4
- Do not modify GEM_PATH once it is set outside of collection.

* Mon Feb 02 2015 Vít Ondruch <vondruch@redhat.com> - 2.0-3
- enable scriptlet requires ruby executable.

* Tue Jan 27 2015 Josef Stribny <jstribny@redhat.com> - 2.0-2
- Update the list of installed gems

* Tue Jan 13 2015 Vít Ondruch <vondruch@redhat.com> - 2.0-1
- Update metapackage from ror40 to rh-ror41.

* Mon Mar 31 2014 Honza Horak <hhorak@redhat.com> - 1.1-4
- Fix path typo in README
  Related: #1063707

* Thu Mar 27 2014 Vít Ondruch <vondruch@redhat.com> - 1.1-3
- Own RubyGems filesystem and manual directories.
  Resolves: rhbz#1080036

* Thu Feb 13 2014 Honza Horak <hhorak@redhat.com> - 1.1-2
- Fix grammar mistakes in README
  Related: rhbz#1058613

* Tue Feb 11 2014 Vít Ondruch <vondruch@redhat.com> - 1.1-1
- Add -build package dependency on scl-utils-build.
  Resolves: rhbz#1058613
- Add LICENSE, README and man page.
  Resolves: rhbz#1063707

* Wed Jan 22 2014 Vít Ondruch <vondruch@redhat.com> - 1-3
- Export GEM_PATH properly.

* Fri Jan 17 2014 Vít Ondruch <vondruch@redhat.com> - 1-2
- Add -scldevel sub-package.
- Automatically generate dependencies on -runtime package.

* Thu Jan 16 2014 Vít Ondruch <vondruch@redhat.com> - 1-1
- Initial package.
