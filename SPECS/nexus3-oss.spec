Summary: Nexus manages software “artifacts” required for development, deployment, and provisioning.
Name: nexus3
Version: 3.6.0
Release: 02
License: AGPL
Group: unknown
URL: http://nexus.sonatype.org/
Source0: %{name}-%{version}-%{release}-unix.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel
AutoReqProv: no

%define __os_install_post %{nil}

%description
A package repository

%prep
%setup -q -n nexus-%{version}-%{release}

%build
%define debug_package %{nil}

%pre
/usr/bin/getent passwd %{name} || /usr/sbin/useradd -r -d /var/lib/%{name} -s /bin/bash %{name}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/%{name}
mv * .install4j $RPM_BUILD_ROOT/usr/share/%{name}
rm -rf $RPM_BUILD_ROOT/usr/share/%{name}/data

mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d/
ln -sf /usr/share/%{name}/bin/nexus $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

mkdir -p $RPM_BUILD_ROOT/etc/
ln -sf /usr/share/%{name}/etc $RPM_BUILD_ROOT/etc/%{name}

# patch work dir
sed -i -e 's/-Dkaraf.data=.*/-Dkaraf.data=\/var\/lib\/%{name}\//' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus.vmoptions
sed -i -e 's/-Djava.io.tmpdir=.*/-Djava.io.tmpdir=\/var\/lib\/%{name}\/tmp\//' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus.vmoptions
mkdir -p $RPM_BUILD_ROOT/var/lib/%{name}

# Patch user
sed -i -e 's/#run_as_user=.*/run_as_user=nexus3/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus.rc

# patch logfiles
mkdir -p $RPM_BUILD_ROOT/var/log/%{name}
sed -i -e 's/karaf.bootstrap.log=.*/karaf.bootstrap.log=\/var\/log\/%{name}\/karaf.log/' $RPM_BUILD_ROOT/usr/share/%{name}/etc/karaf/custom.properties
sed -i -e 's/<File>${karaf.data}\/log\/nexus.log<\/File>/<File>\/var\/log\/%{name}\/%{name}.log<\/File>/' $RPM_BUILD_ROOT/usr/share/%{name}/etc/logback/logback.xml
sed -i -e 's/<File>${karaf.data}\/log\/request.log<\/File>/<File>\/var\/log\/%{name}\/request.log<\/File>/' $RPM_BUILD_ROOT/usr/share/%{name}/etc/logback/logback-access.xml

%preun
service %{name} stop

%postun
rm -f $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc
/etc/rc.d/init.d/%{name}
%attr(-,%{name},%{name}) /etc/%{name}
%attr(-,%{name},%{name}) /var/lib/%{name}
%attr(-,%{name},%{name}) /var/log/%{name}
%attr(-,%{name},%{name}) /usr/share/%{name}

%changelog

* Sat Dec 2 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.6.0-02
- Update to Nexus 3.6.0-02

* Sat Dec 2 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.5.2-01
- Update to Nexus 3.5.2-01

* Sat Dec 2 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.5.1-02
- Update to Nexus 3.5.1-02

* Thu Aug 3 2017 Julio Gonzalez <git@juliogonzalez.es> - 3.5.0-02
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

* Fri Apr 8 2016 Julio Gonzalez <git@juliogonzalez.es> - 3.0.0-03
- Initial packaging for Nexus 3.x
