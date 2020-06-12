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
Name: nexus3
# Remember to adjust the version at Source0 as well. This is required for Open Build Service download_files service
Version: 3.24.0.02
Release: 1%{?dist}
# This is a hack, since Nexus versions are N.N.N-NN, we cannot use hyphen inside Version tag
# and we need to adapt to Fedora/SUSE guidelines
%define nversion %(echo %{version}|sed -r 's/(.*)\\./\\1-/')
License: EPL-2.0
Group: Development/Tools/Other
URL: http://nexus.sonatype.org/
Source0: http://download.sonatype.com/nexus/3/nexus-3.24.0-02-unix.tar.gz
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
%setup -q -n nexus-%{nversion}

%build
%define debug_package %{nil}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/share/%{name}
mv * .install4j $RPM_BUILD_ROOT/usr/share/%{name}
rm -rf $RPM_BUILD_ROOT/usr/share/%{name}/data

%if 0%{?use_systemd}
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

# Support Jetty upgrade from 9.3 to 9.4
sed -i -e '/<Set name="selectorPriorityDelta"><Property name="jetty.http.selectorPriorityDelta" default="0"\/><\/Set>/d' $RPM_BUILD_ROOT/usr/share/%{name}/etc/jetty/jetty-http.xml
sed -i -e '/<Set name="selectorPriorityDelta"><Property name="jetty.http.selectorPriorityDelta" default="0"\/><\/Set>/d' $RPM_BUILD_ROOT/usr/share/%{name}/etc/jetty/jetty-https.xml

# Check if 1.8.0 is the default version, as it is what Nexus expects
JAVA_MAJOR_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f2)
if [ "${JAVA_MAJOR_VERSION}" != "8" ]; then
  echo "WARNING! Default java version does not seem to be 1.8!"
  echo "Keep in mind that Nexus3 is only compatible with Java 1.8.0 at the moment!"
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
if [ $1 -eq 1 ]; then
  echo "Autogenerated password for admin user will be stored at /var/lib/nexus3/admin.password after Nexus startup"
fi

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
%service_del_postun -n %{name}.service
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc
%attr(-,%{name},%{name}) /etc/%{name}
%dir /usr/share/%{name}
%dir /usr/share/%{name}/etc
%config(noreplace) /usr/share/%{name}/etc/*
%doc /usr/share/%{name}/*.txt
/usr/share/%{name}/.install4j
/usr/share/%{name}/bin
/usr/share/%{name}/deploy
/usr/share/%{name}/lib
/usr/share/%{name}/public
/usr/share/%{name}/system
%attr(-,%{name},%{name}) /var/lib/%{name}
%attr(-,%{name},%{name}) /var/log/%{name}
%if 0%{?use_systemd}
%{_unitdir}/%{name}.service
%else
/etc/init.d/%{name}
%endif

%changelog
* Sat Jun 13 2020 Julio González Gil <packages@juliogonzalez.es> - 3.24.0.02-1
- Update to Nexus 3.24.0-02
- Bugfixes:
  * NEXUS-17288: Image broken on logger edit
  * NEXUS-19529: viewing the UI repositories list will trigger s3 blobstore metrics retrieval even if that blobstore is not used
  * NEXUS-23071: /beta/repositories/{format}/group/{repositoryName} example model is wrong
  * NEXUS-23082: Update embedded Java version to latest Java 8
  * NEXUS-23418: rest api proxy repository httpClient authentication does not take effect
  * NEXUS-23551: Yum Authenticating against RHEL servers in AWS
  * NEXUS-23712: items added or removed from yum metadata files when metadata is rebuilt may not be logged
  * NEXUS-23761: beta/repositories/{format}/hosted/{repositoryName} has invalid parameters in example
  * NEXUS-23800: Race condition in lazy maven metadata rebuild causes build failures, slow builds
  * NEXUS-23872: Unable to set repository HTTP client auth via REST
  * NEXUS-23903: long running database queries for docker repositories can lead to thread and db connection pool exhaustion
  * NEXUS-23980: 'USER_ROLE_MAPPING' was not found in database 'component' exceptions seen with docker
- Improvements:
  * NEXUS-23588: Repository Management API missing yum proxy
  * NEXUS-23650: Allow REST API to Enable/Disable Anonymous Access
  * NEXUS-23798: REST API to enable User Tokens
  * NEXUS-23854: Export for Raw and Maven formats (Pro Only)
  * NEXUS-23870: "Node already has an asset" for browse tree rebuild should not fail Transactions status check
  * NEXUS-23897: Memory settings in docker image are too low
  * NEXUS-23970: NuGet v3 Hosted
  * NEXUS-24091: REST API for Cocoapods repositories
  * NEXUS-24092: REST API for Raw repositories
  * NEXUS-24093: REST API for RubyGems repositories

* Wed May  6 2020 Julio González Gil <packages@juliogonzalez.es> - 3.23.0.03-1
- Update to Nexus 3.23.0-03
- Bugfixes:
  * NEXUS-23360: Docker: Infinite loop for authorization to registry.connect.redhat.com
  * NEXUS-23548: Helm Chart Repository API version format incorrect
  * NEXUS-20349: NuGet repository returns multiple versions as islatest=true
  * NEXUS-23420: NonResolvablePackageException thrown when downloading a package through the PyPI group
  * NEXUS-23398: Retrieval of some packages from PyPI fails
  * NEXUS-23487: PyPI repository returns 500 error response if remote returns an invalid response.
  * NEXUS-23379: Invalid content returned through proxy prevents valid content from being retreived
  * NEXUS-23616: Blob Store API allows users to create a blobstore without path
- Improvements:
  * NEXUS-11468: Import for Raw and Maven formats (requires Pro license)
  * NEXUS-16954: Nexus Intelligence via npm audit
  * NEXUS-21087: (Docker) Support OCI registry format
  * NEXUS-23436: Clearer anonymous panel for upgrade wizard

* Fri Apr 17 2020 Julio González Gil <packages@juliogonzalez.es> - 3.22.1.02-1
- Update to Nexus 3.22.1-02
- Bugfixes
  * CVE-2020-11753: Improper access controls allowed privileged user to craft requests in such a manner that scripting tasks could be created,
                    updated or executed without use of the user interface or REST API
  * NEXUS-23281: Requesting a SNAPSHOT artifact from a RELEASE Repo returns HTTP 400
  * NEXUS-23348: SAML - New UI Login SSO Button does not respect the nexus-context-path
  * NEXUS-23352: Conan integration in 3.22.0 does not handle Header Only packages
  * NEXUS-23359: SAML - NPE thrown if IdP metadata does not contain SingleLogoutService element
  * NEXUS-23399: NuGet v3 proxy repository will not serve cached content if remote is blocked
  * NEXUS-23441: Already cached NuGet v2 proxy repository content will return 502 if Component Max Age expires and the remote is not available
  * NEXUS-23504: Privileged user can create, modify and execute scripting tasks
  * NEXUS-23556: CVE-2020-11415: LDAP system credentials can be exposed by admin user
- Improvements:
  * NEXUS-23396: Admin - Cleanup repositories using their associated policies task should lazily mark maven metadata for rebuild

* Sat Mar 28 2020 Julio González Gil <packages@juliogonzalez.es> - 3.22.0.02-1
- Update to Nexus 3.22.0-02
- Bugfixes
  * CVE-2020-11444: Improper access controls allowed authenticated users to craft requests in such a manner that configuration for other
                    users in the system could be affected
  * NEXUS-16159: "Require user tokens for repository authentication" now enforced properly
  * NEXUS-19437: a blobstore in any other state than STARTED cannot be removed
  * NEXUS-21011: Compact blob store task cannot hard delete blob assets when the blobstore is out of space
  * NEXUS-21808: DockerTokenDecoder.dumpToken(String) method may fail to parse docker bearer tokens causing IndexOutOfBoundsException
  * NEXUS-22054: "Repair - reconcile component database from blob store" task does not remove invalid component db references.
  * NEXUS-22245: Cannot Delete NPM Scoped Folder via UI
  * NEXUS-22602: Running metadata rebuild task with GA restrictions fails
  * NEXUS-22666: concurrent uploads to the same maven GA may result in 500 response due to OConcurrentModificationException
  * NEXUS-22669: First staging move to npm hosted repo fails with 500 error.
  * NEXUS-22729: Cleanup Policy task results in removal of maven-metadata from non-timestamped snapshots
  * NEXUS-22760: POST /service/extdirect/poll/rapture_State_get lists all tasks from the database
  * NEXUS-22770: Change in stored Pypi proxy package paths creates duplicate assets and breaks browse node creation
  * NEXUS-22802: AnonymousSettings.jsx does not respect nexus-context-path
  * NEXUS-22853: Too many tasks scheduled if an upgrade requires rebuilding the browse_node table
  * NEXUS-22896: performance regression in search REST API
  * NEXUS-23048: Problem proxying NuGet packages hosted by GitHub Packages
  * NEXUS-23072: Anonymous Access icon missing
  * NEXUS-23104: Offline repositories allow UI upload
  * NEXUS-23236: org.sonatype.nexus.quartz.internal.orient.JobStoreImpl is a concurrency bottleneck
  * NEXUS-23272: Inability to add * permission to user on 3.21.2
- Improvements
  * NEXUS-5716: add a way to configure default privileges for any signed-in users
  * NEXUS-20939: SAML integration
  * NEXUS-22820: Process search index updates in the background in a non-blocking fashion
  * NEXUS-21910: Additional REST provisioning support for npm, NuGet and PyPI repositories

* Tue Mar 24 2020 Julio González Gil <packages@juliogonzalez.es> - 3.21.2.03-1
- Update to Nexus 3.21.2-03
- Bugfixes
  * NEXUS-23205: Disabled Groovy Scripting By Default. In order to make NXRM more secure, Groovy scripting
                 engine is now disabled by default. This affects Groovy scripts as used through the REST API
                 and through scheduled tasks. Scripts which are present from an upgraded version will
                 continue to be executable but their script source will not editable.
                 For more information (including how to re-enable Groovy scripting), see
                 https://issues.sonatype.org/browse/NEXUS-23205

* Sat Feb 29 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.21.1.01-1
- Update to Nexus 3.21.1-01
- Remove a broken menu entry incorrectly appearing for some users

* Sat Feb 29 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.21.0.05-1
- Update to Nexus 3.21.0-05
- Bugfixes:
  * NEXUS-18186: Disabling redeploy for a private Docker repo breaks the "latest" tag
  * NEXUS-21730: Audit log does not log all attributes for repository change events
  * NEXUS-21329: "Remove a member from a blob store group" task processes missing files in the source blob store
  * NEXUS-18905: Cleanup tasks fail with "No search context found for id" error
  * NEXUS-13306: Usernames containing non URL safe characters cannot authenticate using the Crowd realm 
  * NEXUS-16009: Browse tree for NuGet proxy repositories shows packages that are not locally cached
  * NEXUS-22051: PyPI group merge is not case sensitive
  * NEXUS-22351: R PACKAGES file lost on upgrade to 3.20.x
  * NEXUS-17477: Unable to install hosted gem which has multiple version requirements
  * NEXUS-22052: Yum Metadata not rebuilt after staging deletion of rpm
- Improvements:
  * NEXUS-11730: Support for proxying p2 repositories. p2 is a technology for provisioning and managing
                 Eclipse- and Equinox-based applications
  * NEXUS-13325: Helm is the first application package manager running atop Kubernetes(k8s). It allows
                 describing the application structure through convenient helm-charts and managing it with
                 simple commands
  * NEXUS-10886: NuGet V3 Proxy support gives Nexus Repository Manager users access to the up-to-date
                 V3 API. This is the first part of a wider initiative to bring full V3 support, group and
                 hosted will follow in future releases
  * NEXUS-16251: Provide a common facility to allow RPM clients to get GPG keys to verify package
                 signatures in remote repositories.
  * NEXUS-13434: Provide npm cli ping support

* Fri Feb 28 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.20.1.01-2
- Clean up spec and fix to build all distributions at OpenBuildService
- Enable building and installation for Amazon Linux >= 2
- Enable building and installation for for openSUSE Tumbleweed/Factory

* Mon Jan 27 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.20.1.01-1
- Update to Nexus 3.20.1-01
- Bugfixes:
  * NEXUS-22249: An error may occur when starting NXRM Pro due to race condition around the license loading.
  * NEXUS-22241: During the upgrade process from older releases (3.19.0 and before), NXRM may throw an exception
                 when updating PyPI database configuration.

* Mon Jan 27 2020 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.20.0.04-1
- License for Nexus OSS is EPL-2.0 as stated at https://blog.sonatype.com/2012/06/nexus-oss-switched-to-the-eclipse-public-license-a-clarification-and-an-observation/
  and it is since 2012. Mistake inherited from the original packages from Jens Braeuer.
- Update to Nexus 3.20.0-04
- Bugfixes
  * NEXUS-21311: Yum and CentOS 8
  * NEXUS-21371: npm package metadata does not return correct status code sometimes
  * NEXUS-19811: Offline and misconfigured blob store should be noted in UI
  * NEXUS-21368: Proxy repository removes get-params from HTTP sources
  * NEXUS-22144: Slow performance displaying content selectors in UI
  * NEXUS-21306: Cannot proxy Docker repository on Bintray
  * NEXUS-21315: Extremely slow processing in "Docker - Delete unused manifests and images" task
  * NEXUS-21672: Group repo with proxy repo member to remote group repo responds 404 when remote group repo responds
                 "403 Requested item is quarantined"
  * NEXUS-18117: PyPI ignoring python_requires metadata
  * NEXUS-20705: Index can contain absolute URLs which bypass Nexus Repository Manager
  * NEXUS-21589: Repository health check can fail if the same asset exists in more than one repository
  * NEXUS-14233: Support managing Realms via the REST API
  * NEXUS-21138: Snapshot remover leaves maven-metadata.xml files deleted for a long time, breaking builds
  * NEXUS-12488: Remote https repository with TLS client certificate loaded in NXRM JVM keystore not trusted
  * NEXUS-20140: 500 Server Error shown in Chrome console when accessing Support Status page
- Improvements
  * NEXUS-20269: jetty-http-redirect-to-https.xml removed and its use discouraged
                 Startup will fail if your configuration references jetty-http-redirect-to-https.xml
                 Check https://support.sonatype.com/hc/en-us/articles/360037845633 if that is the case
  * NEXUS-19424 : Ability to Clean Up by "Never downloaded"
  * NEXUS-9837: R Format Support
  * NEXUS-12456: Enhanced npm login for private repository usages
  * NEXUS-13433: npm whoami support
  * NEXUS-20268: HSTS enabled by default for Inbound Jetty HTTPS connectors
                 See https://support.sonatype.com/hc/en-us/articles/360024943193

* Thu Oct 17 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.19.1.01-1
- Update to Nexus 3.19.1-01
- Bugfixes
  * NEXUS-21381: Prevent Docker Proxy Repository throwing null pointer exceptions and blocking some image pulls
                 after upgrade

* Thu Oct 17 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.19.0.01-1
- Update to Nexus 3.19.0-01
- Bugfixes
  * NEXUS-10679: NPM repos don't handle HEAD requests
  * NEXUS-19102: Unable to proxy private Azure (ACR) registry
- Improvements
  * NEXUS-19970: CocoaPods Format Support
  * NEXUS-19866: Conda Format Support
  * NEXUS-9862: New abilities for adding and removing "distribution tags" into npm metadata via the npm CLI
  * NEXUS-17797: S3 peerformance improvements, support for encrypted S3 buckets, use of custom encryption keys,
                 simplified permission testing, and essential improvements to storage space metrics
  * NEXUS-19120: Added support for Docker Foreign Layers. Nexus Repository Manager users can now proxy docker images
                 with foreign layers when pulling Microsoft Windows images.
  * NEXUS-19144, NEXUS-19142, NEXUS-19143, NEXUS-19145, NEXUS-19146, NEXUS-16734:  Enhanced REST API endpoints for
                 initial provisioning and maintenance of Nexus Repository Manager
  * NEXUS-20682: Go Format Data Integration
  * NEXUS-19525: Multi-policy Cleanup

* Tue Aug 20 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.18.1.01-1
- Update to Nexus 3.18.1-01
- Bugfixes
  * NEXUS-20674: Fixed an exception occurring when a user manually logs out of the user interface.
  * NEXUS-19235: Propagates the quarantine status code when NXRM proxies another NXRM with Firewall enabled.

* Mon Aug 19 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.18.0.01-1
- Update to Nexus 3.18.0-01
- Bugfixes
  * NEXUS-10252: "Invalid authentication ticket" error on password change
  * NEXUS-14729: Regression: Nexus 3 returns 501, 400 and 204 responses for MKCOL requests
  * NEXUS-15878: UI poll requests iterates over all privileges.
  * NEXUS-19618: Expensive, error prone check done for content validation of checksums
  * NEXUS-20014: browse operations can be slower than expected with many content selectors
  * NEXUS-20104: OrientDB database backups default compression level and buffer size are not optimized
  * NEXUS-20139: Repair - Rebuild repository search queries are not optimized, potentially impacting other search operations
  * NEXUS-20360: request.log is no longer included in support zips
  * NEXUS-20453: Browse operations can be very slow when using content selector permissions
  * NEXUS-20479: Stored XSS Vulnerabilities (eventually public)
- Improvements
  * NEXUS-19954: Increase the default maximum heap and direct memory sizes
  * NEXUS-20100: allow customizing compression level and buffer size of Orient database checkpoint during upgrade using system properties

* Fri Aug 16 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.17.0.01-1
- Update to Nexus 3.17.0-01
- Password for admin user at new installations is now random and can be found
  at /var/lib/nexus3/admin.password (https://help.sonatype.com/repomanager3/installation/post-install-checklist
  for more details) 

* Fri Aug 16 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.16.2.01-1
- Update to Nexus 3.16.2-01

* Fri Apr 26 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.16.1.02-1
- Update to Nexus 3.16.1-02

* Fri Apr 26 2019 Julio Gonzalez Gil <packages@juliogonzalez.es> - 3.16.0.01-1
- Update to Nexus 3.16.0-01

* Tue Mar 12 2019 Julio Gonzalez Gil <git@juliogonzalez.es> 3.15.2.01-1
- Update to Nexus 3.15.2-01

* Sat Jan 26 2019 Angelo Verona <angelo@verona.one> - 3.15.1.01-1
- Update to Nexus 3.15.1-01
- Do not replace modified config files

* Mon Jan 14 2019 Angelo Verona <angelo@verona.one> - 3.15.0.01-1
- Update to Nexus 3.15.0-01

* Mon Oct 29 2018 Wojciech Urbański <mail@wurbanski.me> - 3.14.0.04-1
- Update to Nexus 3.14.0-04

* Tue Sep 4 2018 Wojciech Urbański <mail@wurbanski.me> - 3.13.0.01-1
- Update to Nexus 3.13.0-01

* Mon Jun 25 2018 Julio Gonzalez <git@juliogonzalez.es> - 3.12.1.01-1
- Update to Nexus 3.12.1-01

* Sat May 26 2018 Anton Patsev <patsev.anton@gmail.com> - 3.12.0.01-1
- Update to Nexus 3.12.0-01

* Fri May 11 2018 Anton Patsev <patsev.anton@gmail.com> - 3.11.0.01-1
- Update to Nexus 3.11.0-01

* Fri Apr 20 2018 Pavel Zhbanov <pzhbanov@luxoft.com> - 3.10.0.04-1
- Update to Nexus 3.10.0-04

* Sat Mar 10 2018 Julio Gonzalez <git@juliogonzalez.es> - 3.9.0.01-1
- Update to Nexus 3.9.0-01

* Sat Mar 10 2018 Julio Gonzalez <git@juliogonzalez.es> - 3.8.0.02-1
- Update to Nexus 3.8.0-02

* Tue Jan 02 2018 Julio Gonzalez <git@juliogonzalez.es> - 3.7.1.02-1
- Update to Nexus 3.7.1-02

* Tue Jan 02 2018 Julio Gonzalez <git@juliogonzalez.es> - 3.7.0.04-1
- Update to Nexus 3.7.0-04
- Warning: 3.7.0-04.1 is affected by issue 
  https://issues.sonatype.org/browse/NEXUS-15278, it is highly recommended
  you install 3.7.1-02-1 if you have offline repositories

* Sat Dec 30 2017 Anton Patsev <patsev.anton@gmail.com> - 3.6.2.01-2
- Stop requiring sysvinit compatibility for systemd
- Add systemd service

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
