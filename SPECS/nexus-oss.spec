%define __os_install_post %{nil}

%if 0%{?suse_version}
%define chkconfig_cmd /usr/bin/chkconfig
%else
%define chkconfig_cmd /sbin/chkconfig
%endif

# Use systemd for fedora >= 18, rhel >=7, SUSE >= 12 SP1 and openSUSE >= 42.1
%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7) || (!0%{?is_opensuse} && 0%{?suse_version} >=1210) || (0%{?is_opensuse} && 0%{?sle_version} >= 120100)

Summary: Nexus manages software “artifacts” required for development, deployment, and provisioning.
Name: nexus
# Remember to adjust the version at Source0 as well. This is required for Open Build Service download_files service
Version: 2.14.11.01
Release: 1%{?dist}
# This is a hack, since Nexus versions are N.N.N-NN, we cannot use hyphen inside Version tag
# and we need to adapt to Fedora/SUSE guidelines
%define nversion %(echo %{version}|sed -r 's/(.*)\\./\\1-/')
License: AGPL
Group: unknown
URL: http://nexus.sonatype.org/
Source0: http://www.sonatype.org/downloads/%{name}-2.14.11-01-bundle.tar.gz
Source1: %{name}.service
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires: java >= 1.7.0
AutoReqProv: no

%description
A package repository

%prep
%setup -q -n %{name}-%{nversion}

%build
%define debug_package %{nil}

%pre
/usr/bin/getent passwd %{name} > /dev/null || /usr/sbin/useradd -r -d /var/lib/%{name} -U -s /bin/bash %{name}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/%{name}
mv * $RPM_BUILD_ROOT/usr/share/%{name}

%if %{use_systemd}
%{__mkdir} -p %{buildroot}%{_unitdir}
%{__install} -m644 %{SOURCE1} \
    %{buildroot}%{_unitdir}/%{name}.service
%else
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
ln -sf /usr/share/%{name}/bin/nexus $RPM_BUILD_ROOT/etc/init.d/%{name}
%endif

mkdir -p $RPM_BUILD_ROOT/etc/
ln -sf /usr/share/%{name}/conf $RPM_BUILD_ROOT/etc/%{name}

# patch work dir
sed -i -e 's/%{name}-work=.*/%{name}-work=\/var\/lib\/%{name}\//' $RPM_BUILD_ROOT/usr/share/%{name}/conf/nexus.properties
mkdir -p $RPM_BUILD_ROOT/var/lib/%{name}

# patch pid dir
sed -i -e 's/PIDDIR=.*/PIDDIR=\/var\/run\/%{name}/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus
mkdir -p $RPM_BUILD_ROOT/var/run/%{name}

# Patch user
sed -i -e 's/#RUN_AS_USER=.*/RUN_AS_USER=%{name}/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus

# patch logfile
mkdir -p $RPM_BUILD_ROOT/var/log/%{name}
sed -i -e 's/wrapper.logfile=.*/wrapper.logfile=\/var\/log\/%{name}\/%{name}.log/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/jsw/conf/wrapper.conf

# Since java is a virtual package, we can only check that >= 1.8.0 is installed, but not < 1.9
# Also it is possible that despite 1.8.0 is installed, it is not the default version, so we check
# for it
JAVA_MAJOR_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f2)
if [ "${JAVA_MAJOR_VERSION}" != "8" ]; then
  echo "WARNING! Default java version does not seem to be 1.8!"
  echo "Keep in mind that Nexus3 is only compatible with Java 1.8.0 at the moment!"
  echo "Tip: Check if 1.8 is installed and use (as root):"
  echo "update-alternatives --config java"
  echo "to adjust the default version to be used"
fi


%post
%if %use_systemd
/usr/bin/systemctl daemon-reload
%else
%{chkconfig_cmd} --add %{name}
%endif

%preun
%if %use_systemd
/usr/bin/systemctl stop %{name}
%else
/etc/init.d/%{name} stop
%{chkconfig_cmd} --del %{name}
%endif

%postun
%if %use_systemd
/usr/bin/systemctl daemon-reload
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc
%attr(-,%{name},%{name}) /etc/%{name}
%attr(-,%{name},%{name}) /var/lib/%{name}
%attr(-,%{name},%{name}) /var/log/%{name}
%attr(-,%{name},%{name}) /var/run/%{name}
%attr(-,%{name},%{name}) /usr/share/%{name}
%if %{use_systemd}
%{_unitdir}/%{name}.service
%else
/etc/init.d/%{name}
%endif

%changelog
* Fri Nov 23 2018 Julio Gonzalez <git@juliogonzalez.es> - 2.14.11.01-1
- Update to 2.14.11-01
- Require Java 1.8.0

* Fri Nov 23 2018 Julio Gonzalez <git@juliogonzalez.es> - 2.14.10.01-1
- Update to 2.14.10-01

* Fri Nov 23 2018 Julio Gonzalez <git@juliogonzalez.es> - 2.14.9.01-1
- Update to 2.14.9-01 

* Sat Mar 10 2018 Julio Gonzalez <git@juliogonzalez.es> - 2.14.8.01-1
- Update to 2.14.8-01

* Sat Mar 10 2018 Julio Gonzalez <git@juliogonzalez.es> - 2.14.7.01-1
- Update to 2.14.7-01
- Compatibility with Java 1.7.0 is restored

* Sat Mar 10 2018 Julio Gonzalez <git@juliogonzalez.es> - 2.14.6.02-1
- Update to 2.14.6-02

* Sat Dec 30 2017 Anton Patsev <patsev.anton@gmail.com> - 2.14.5.02-2
- Stop requiring sysvinit compatibility for systemd
- Add systemd service

* Thu Dec 28 2017 Julio Gonzalez <git@juliogonzalez.es> - 2.14.5.02-1
- Start using Fedora/RHEL release conventions
- Fix problems on RPM removals
- Require Java 1.8.0
- Fix source
- Make the package compatible with SUSE and openSUSE

* Thu Aug  3 2017 Julio Gonzalez <git@juliogonzalez.es> - 2.14.5-02
- Update to 2.14.5-02

* Sat May 20 2017 Julio Gonzalez <git@juliogonzalez.es> - 2.14.4-03
- Update to 2.14.4-03

* Sat May 20 2017 Julio Gonzalez <git@juliogonzalez.es> - 2.14.3-02
- Update to 2.14.3-02

* Sat May 20 2017 Julio Gonzalez <git@juliogonzalez.es> - 2.14.2-01
- Update to 2.14.2-01

* Sat Nov 12 2016 Julio Gonzalez <git@juliogonzalez.es> - 2.14.1-01
- Update to 2.14.1-01

* Sun May 29 2016 Julio Gonzalez <git@juliogonzalez.es> - 2.13.0-01
- Update to 2.13.0-01

* Sat Feb 13 2016 Julio Gonzalez <git@juliogonzalez.es> - 2.12.0-01
- Update to 2.12.0-01

* Tue Jul 21 2015 Julio Gonzalez <git@juliogonzalez.es> - 2.11.4-01
- Update to 2.11.4-01

* Fri Jun 26 2015 Julio Gonzalez <git@juliogonzalez.es> - 2.11.3-01
- Update to last version available
- Nexus will now listen at 8081 (this can be modified at
  /etc/nexus/nexus.properties)
- Nexus runs now without as system user, not as root
- Remove jdk dependency (no virtual package at CentOS 7)

* Thu Dec 22 2011 Jens Braeuer <braeuer.jens@googlemail.com> - 1.9.2.3-1
- Initial packaging.
- For now nexus will run as root and listen to port 80

