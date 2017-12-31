%define __os_install_post %{nil}

%if 0%{?suse_version}
%define chkconfig_cmd /usr/bin/chkconfig
%else
%define chkconfig_cmd /sbin/chkconfig
%endif

# Use systemd for fedora >= 18, rhel >=7, SUSE >= 12 SP1 and openSUSE >= 42.1
%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7) || (!0%{?is_opensuse} && 0%{?suse_version} >=1210) || (0%{?is_opensuse} && 0%{?sle_version} >= 120100)

Summary: Nexus manages software “artifacts” required for development, deployment, and provisioning.
Name: nexus3
Version: 3.6.2.01
Release: 2%{?dist}
# This is a hack, since Nexus versions are N.N.N-NN, we cannot use hyphen inside Version tag
# and we need to adapt to Fedora/SUSE guidelines
%define nversion %(echo %{version}|sed -r 's/(.*)\\./\\1-/')
License: AGPL
Group: unknown
URL: http://nexus.sonatype.org/
Source0: http://download.sonatype.com/nexus/3/%{name}-%{nversion}-unix.tar.gz
Source1: %{name}.service
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
# As soon as we implement a systemd service, this ugly require can be removed
%if %use_systemd
%if (!0%{?is_opensuse} && 0%{?suse_version} >=1210) || (0%{?is_opensuse} && 0%{?sle_version} >= 120100)
Requires: systemd-sysvinit
%else
Requires: systemd-sysv
%endif
%endif
Requires: java >= 1.8.0
AutoReqProv: no

%description
A package repository

%prep
%setup -q -n nexus-%{nversion}

%build
%define debug_package %{nil}

%pre
/usr/bin/getent passwd %{name} > /dev/null || /usr/sbin/useradd -r -d /var/lib/%{name} -U -s /bin/bash %{name}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/%{name}
mv * .install4j $RPM_BUILD_ROOT/usr/share/%{name}
rm -rf $RPM_BUILD_ROOT/usr/share/%{name}/data

%if %{use_systemd}
%{__mkdir} -p %{buildroot}%{_unitdir}
%{__install} -m644 %{SOURCE1} \
    %{buildroot}%{_unitdir}/%{name}.service
%else
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
ln -sf /usr/share/%{name}/bin/nexus $RPM_BUILD_ROOT/etc/init.d/%{name}
%endif

mkdir -p $RPM_BUILD_ROOT/etc/
ln -sf /usr/share/%{name}/etc $RPM_BUILD_ROOT/etc/%{name}

# patch work dir
sed -i -e 's/-Dkaraf.data=.*/-Dkaraf.data=\/var\/lib\/%{name}\//' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus.vmoptions
sed -i -e 's/-Djava.io.tmpdir=.*/-Djava.io.tmpdir=\/var\/lib\/%{name}\/tmp\//' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus.vmoptions
mkdir -p $RPM_BUILD_ROOT/var/lib/%{name}

# Patch user
sed -i -e 's/#run_as_user=.*/run_as_user=%{name}/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus.rc

# patch logfiles
mkdir -p $RPM_BUILD_ROOT/var/log/%{name}
sed -i -e 's/karaf.bootstrap.log=.*/karaf.bootstrap.log=\/var\/log\/%{name}\/karaf.log/' $RPM_BUILD_ROOT/usr/share/%{name}/etc/karaf/custom.properties
sed -i -e 's/<File>${karaf.data}\/log\/nexus.log<\/File>/<File>\/var\/log\/%{name}\/%{name}.log<\/File>/' $RPM_BUILD_ROOT/usr/share/%{name}/etc/logback/logback.xml
sed -i -e 's/<File>${karaf.data}\/log\/request.log<\/File>/<File>\/var\/log\/%{name}\/request.log<\/File>/' $RPM_BUILD_ROOT/usr/share/%{name}/etc/logback/logback-access.xml

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
%attr(-,%{name},%{name}) /usr/share/%{name}
%if %{use_systemd}
%{_unitdir}/%{name}.service
%else
/etc/init.d/%{name}
%endif

%changelog
* Thu Dec 28 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.6.2.01-1
- Start using Fedora/RHEL release conventions
- Fix problems on RPM removals
- Make the package compatible with SUSE and openSUSE

* Sun Dec 24 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.6.2-01
- Update to Nexus 3.6.2-01

* Sat Dec  2 2017 Anton Patsev <apatsev@luxoft.com> - 3.6.0-01
- Update to Nexus 3.6.1-02
- Fix source
- Use package name to configure user to run Nexus
- Require Java 1.8.0

* Sat Dec  2 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.6.0-02
- Update to Nexus 3.6.0-02

* Sat Dec  2 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.5.2-01
- Update to Nexus 3.5.2-01

* Sat Dec  2 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.5.1-02
- Update to Nexus 3.5.1-02

* Thu Aug  3 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.5.0-02
- Update to Nexus 3.5.0-02

* Sat Jul 29 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.4.0-02
- Update to Nexus 3.4.0-02

* Sat Jul 29 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.3.2-02
- Update to Nexus 3.3.2-02

* Sat May 20 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.3.1-01
- Update to Nexus 3.3.1-01

* Sat May 20 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.3.0-01
- Update to Nexus 3.3.0-01

* Sat May 20 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.2.1-01
- Update to Nexus 3.2.1-01

* Sat May 20 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.2.0-01
- Update to Nexus 3.2.0-01

* Sat Nov 12 2016 Julio Gonzalez <git@juliogonzalez.es> - 3.1.0-04
- Update to Nexus 3.1.0-04

* Fri Apr  8 2016 Julio Gonzalez <git@juliogonzalez.es> - 3.0.0-03
- Initial packaging for Nexus 3.x
