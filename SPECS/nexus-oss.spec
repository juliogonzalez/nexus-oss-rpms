%define __os_install_post %{nil}

%if 0%{?suse_version}
%define chkconfig_cmd /usr/bin/chkconfig
%define java_package java-1_8_0-openjdk
%else
%define chkconfig_cmd /sbin/chkconfig
%define java_package java-1.8.0-openjdk
%endif

# Use systemd for SUSE >= 12 SP1 openSUSE >= 42.1, openSUSE Tumbleweed/Factory, fedora >= 18, rhel >=7 and Amazon Linux >= 2
%if (!0%{?is_opensuse} && 0%{?suse_version} >=1210) || (0%{?is_opensuse} && 0%{?sle_version} >= 120100) || 0%{?suse_version} > 1500
%define suse_systemd 1
%endif
%if (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7) || 0%{?amzn} >= 2
%define redhat_systemd 1
%endif
%if 0%{?suse_systemd} || 0%{?redhat_systemd}
%define use_systemd 1
%endif

Summary: Nexus manages software "artifacts" and repositories for them
Name: nexus
# Remember to adjust the version at Source0 as well. This is required for Open Build Service download_files service
Version: 2.15.2.03
Release: 1%{?dist}
# This is a hack, since Nexus versions are N.N.N-NN, we cannot use hyphen inside Version tag
# and we need to adapt to Fedora/SUSE guidelines
%define nversion %(echo %{version}|sed -r 's/(.*)\\./\\1-/')
License: EPL-2.0
Group: Development/Tools/Other
URL: http://nexus.sonatype.org/
Source0: https://download.sonatype.com/%{name}/oss/%{name}-2.15.2-03-bundle.tar.gz
Source1: %{name}.service
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires: %{java_package}
%if 0%{?use_systemd}
Requires: systemd
%endif
AutoReqProv: no

%description
Nexus manages software "artifacts" and repositories required for development,
deployment, and provisioning.

Among others, it can manage JAR or RPM artifactories inside mvn/ivy2 or yum
repositories respectively

Full sources are available at https://github.com/sonatype/nexus-public/archive/release-%{nversion}.tar.gz

%prep
%setup -q -n %{name}-%{nversion}

%build
%define debug_package %{nil}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/%{name}
# Remove all non GNU/Linux stuff
rm -rf bin/jsw/windows* bin/jsw/solaris-* bin/jsw/lib/libwrapper-solaris-* bin/nexus.bat
mv * $RPM_BUILD_ROOT/usr/share/%{name}

%if 0%{?use_systemd}
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
sed -i -e 's/%{name}-work=.*/%{name}-work=\/var\/lib\/%{name}/' $RPM_BUILD_ROOT/usr/share/%{name}/conf/nexus.properties
mkdir -p $RPM_BUILD_ROOT/var/lib/%{name}

# patch pid dir
sed -i -e 's/PIDDIR=.*/PIDDIR=\/var\/lib\/%{name}\/run/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus
mkdir -p $RPM_BUILD_ROOT/var/lib/%{name}/run

# Patch user
sed -i -e 's/#RUN_AS_USER=.*/RUN_AS_USER=%{name}/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/nexus

# patch tmpdir
sed -i -e 's/wrapper.java.additional.1=-Djava.io.tmpdir=.\/.*/wrapper.java.additional.1=-Djava.io.tmpdir=\/tmp/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/jsw/conf/wrapper.conf
rm -rf $RPM_BUILD_ROOT/usr/share/%{name}/tmp

# Patch logfile
sed -i -e 's/wrapper.logfile=.*/wrapper.logfile=\/var\/log\/%{name}\/%{name}.log/' $RPM_BUILD_ROOT/usr/share/%{name}/bin/jsw/conf/wrapper.conf
mkdir -p $RPM_BUILD_ROOT/var/log/%{name}
rm -rf $RPM_BUILD_ROOT/usr/share/%{name}/logs

# Check if 1.8.0 is the default version, as it is what Nexus expects
JAVA_MAJOR_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f2)
if [ "${JAVA_MAJOR_VERSION}" != "8" ]; then
  echo "WARNING! Default java version does not seem to be 1.8!"
  echo "Keep in mind that Nexus2 is only compatible with Java 1.8.0 at the moment!"
  echo "Tip: Check if 1.8 is installed and use (as root):"
  echo "update-alternatives --config java"
  echo "to adjust the default version to be used"
fi

%pre
/usr/bin/getent passwd %{name} > /dev/null || /usr/sbin/useradd -r -d /var/lib/%{name} -U -s /bin/bash %{name}
%if 0%{?suse_systemd}
%service_add_pre %{nexus}.service
%endif

%post
%if 0%{?suse_systemd}
%service_add_post %{name}.service
%endif
%if 0%{?redhat_systemd}
%systemd_post %{name}.service
%endif

%preun
%if 0%{?use_systemd}
%if 0%{?suse_systemd}
%service_del_preun %{name}.service
%endif
%if 0%{?redhat_systemd}
%systemd_preun %{name}.service
%endif
%else
# Package removal, not upgrade
if [ $1 = 0 ]; then
    /sbin/service %{name} stop > /dev/null 2>&1
    %{chkconfig_cmd} --del %{name}
fi
%endif

%postun
%if 0%{?redhat_systemd}
%systemd_postun %{name}.service
%endif
%if 0%{?suse_systemd}
%if 0%{?suse_version} > 1500
%service_del_postun_without_restart %{name}.service
%else
%service_del_postun -n %{name}.service
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%attr(-,%{name},%{name}) /etc/%{name}
%dir /usr/share/%{name}
%dir /usr/share/%{name}/conf
%config(noreplace) /usr/share/%{name}/conf/*
%doc /usr/share/%{name}/*.txt
/usr/share/%{name}/bin
/usr/share/%{name}/lib
/usr/share/%{name}/nexus
%dir %attr(-,%{name},%{name}) /var/lib/%{name}
%dir %attr(-,%{name},%{name}) /var/lib/%{name}/run
%dir %attr(-,%{name},%{name}) /var/log/%{name}
%if 0%{?use_systemd}
%{_unitdir}/%{name}.service
%else
/etc/init.d/%{name}
%endif

%changelog
* Fri Nov 15 2024 Julio González Gil <packages@juliogonzalez.es> - 2.15.2-03-1
- Update to 2.15.2-03
- WARNING: Sonatype will officially sunset its Nexus Repository 2 product on
           June 30, 2025. Consider migrating to Nexus Repository 3 as soon as
           possible:
           https://help.sonatype.com/en/upgrading-from-nexus-repository-manager-2.html
           Find more information at the Sonatype Nexus Repository 2 Sunsetting
           Information help page:
           https://download.sonatype.com/nexus/2/Sonatype%20Nexus%20Repository%202%20Help.pdf
- Bugfixes:
  * CVE-2024-5082: Fixed a Remote Code Execution vulnerability through which
                   an attacker with privileges to publish content could upload
                   a specially crafted file that would result in Nexus
                   Repository attempting to execute embedded commands
                   upon retrieval
  * CVE-2024-5083: Fixed a Stored XSS vulnerability through which an attacker
                   with privileges to publish content could upload a specially
                   crafted file that includes embedded JavaScript. If that
                   file is viewed by an authenticated user, the JavaScript
                   could execute product features available to the
                   authenticated user

* Thu Oct 12 2023 Julio González Gil <packages@juliogonzalez.es> - 2.15.1-02-3
- Fix the macro for the service removal so the package builds again for
  openSUSE Tumbleweed and Factory

* Fri Aug 26 2022 Julio González Gil <packages@juliogonzalez.es> - 2.15.1-02-2
- Update the URL for the sources, as the previous one returns a HTTP 503

* Thu Mar 24 2022 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.15.1-02-1
- Update to 2.15.1-02
- Bugfixes:
  * Correct a regression introduce in 2.15.0 that prevented writing the request
    log

* Fri Mar 18 2022 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.15.0-04-1
- Update to 2.15.0-04
- Bugfixes:
  * Resolved npm Memory Issue: You must set the property for
    nexus.npm.abbreviateMetadata to "True" in
    $NEXUS_HOME/conf/nexus.properties to enable the fix.
    Enabling this property may affect what the CLI shows, but it will improve
    performance when dealing with large metadata.
  * Fixed Performance Issue
- Features:
  * Upgraded to Jetty 9.4 from Jetty 8: Adminstrators who have customized
    their Jetty configuration will need to make changes before they can
     upgrade to this release. See the knowledge base for mroe information:
     https://support.sonatype.com/hc/en-us/articles/4417117321619-Eclipse-Jetty-Changes-in-Repository-2-15-0
  * Add Ext JS Licensing Declaration to Nexus Repository 2
  * Upgraded Goodies Library (prevents potential security
    vulnerability CVE-2020-15870)

* Sat Dec 18 2021 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.21-02-1
- Update to 2.14.21-02
- Bugfixes:
  * logback library update to fix a low/moderate vulnerability, as a precautionary
    measure. No known exploit of Nexus Repository via logback at this time.

* Tue Jan  5 2021 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.20-02-1
- Update to 2.14.20-02
- Bugfixes:
  * NEXUS-26224: CVE-2020-13920: Apache ActiveMQ JMX is vulnerable to a MITM attack
  * NEXUS-25956: Signatures with ECC algorithm not being recognized

* Fri Oct  2 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.19.01-1
- Update to 2.14.19-01
- Bugfixes:
  * Minor security fixes.

* Fri Oct  2 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.18.01-1
- Update to 2.14.18-01
- Bugfixes:
  * NEXUS-21802: Maven metadata sha256/sha512 checksum in staging repositories

* Fri Apr 17 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.17.01-1
- Update to 2.14.17-01
- Bugfixes:
  * NEXUS-23556: CVE-2020-11415: LDAP system credentials can be exposed by admin user

* Fri Feb 28 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.16.01-2
- Clean up spec and fix to build all distributions at OpenBuildService
- Enable building and installation for Amazon Linux >= 2
- Enable building and installation for for openSUSE Tumbleweed/Factory

* Mon Jan 27 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.16.01-1
- License for Nexus OSS is EPL-2.0 as stated at https://blog.sonatype.com/2012/06/nexus-oss-switched-to-the-eclipse-public-license-a-clarification-and-an-observation/
  and it is since 2012. Mistake inherited from the original packages from Jens Braeuer.
- Update to 2.14.16-01
- Bugfixes:
  * NEXUS-22014: CVE-2019-15893: Remote Code Execution vulnerability
  * NEXUS-22453: Update Apache Shiro library to resolve security vulnerability
  * NEXUS-22313: Invalid content-range header returned
  * NEXUS-13306: usernames containing non URL safe characters cannot authenticate using the Crowd realm

* Thu Oct 17 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.15.01-1
- Update to 2.14.15-01
- Bugfixes:
  * NEXUS-21044: CVE-2019-15893: Remote Code Execution vulnerability
  * NEXUS-21193: CVE-2019-16530: Remote Code Execution vulnerability
  * NEXUS-20626: CVE-2019-5475: OS Command Injection vulnerability (second part to the fix in 2.14.14)
  * NEXUS-21512: Update Apache Tika and Commons Compress libraries to resolve security vulnerabilities

* Fri Aug 16 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.14.01-1
- Update to 2.14.14-01

* Fri Apr 26 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.13.01-1
- Update to 2.14.13-01

* Tue Mar 12 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 2.14.12.02-1
- Update to 2.14.12-02

* Sat Jan 26 2019 Julio Gonzalez <packages@juliogonzalez.es> - 2.14.11.01-2
- Do not replace modified config files

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

