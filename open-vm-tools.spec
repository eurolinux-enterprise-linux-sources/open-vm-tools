################################################################################
### Copyright 2013-17 VMware, Inc.  All rights reserved.
###
### RPM SPEC file for building open-vm-tools packages.
###
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of version 2 of the GNU General Public License as
### published by the Free Software Foundation.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
################################################################################

%global _hardened_build 1
%global majorversion    10.1
%global minorversion    5
%global toolsbuild      5055683
%global toolsversion    %{majorversion}.%{minorversion}
%global toolsdaemon     vmtoolsd
%global vgauthdaemon    vgauthd

Name:             open-vm-tools
Version:          %{toolsversion}
Release:          3%{?dist}
Summary:          Open Virtual Machine Tools for virtual machines hosted on VMware
Group:            Applications/System
License:          GPLv2
URL:              https://github.com/vmware/%{name}
Source0:          https://github.com/vmware/%{name}/releases/download/stable-%{version}/%{name}-%{version}-%{toolsbuild}.tar.gz
Source1:          %{toolsdaemon}.service
Source2:          %{vgauthdaemon}.service
%if 0%{?rhel} >= 7
ExclusiveArch:    x86_64
%else
ExclusiveArch:    %{ix86} x86_64
%endif

Patch1:           glibc-sysmacros.patch

BuildRequires:    autoconf
BuildRequires:    automake
BuildRequires:    libtool
BuildRequires:    gcc-c++
BuildRequires:    doxygen
# Fuse is optional and enables vmblock-fuse
BuildRequires:    fuse-devel
BuildRequires:    glib2-devel >= 2.14.0
BuildRequires:    gtk2-devel >= 2.4.0
%if 0%{?fedora} >= 23
# F23 split gdk-pixbuf2-devel >= 2.31.3-5 into 3 packages,
# gdk-pixbuf2-devel, gdk-pixbuf2-modules-devel, and
# gdk-pixbuf2-xlib-devel. gtk2-devel does not depend on
# gdk-pixbuf2-xlib-devel. Therefore, we need to pull in
# gdk-pixbuf2-xlib-devel dependency ourselves.
BuildRequires:    gdk-pixbuf2-xlib-devel
%endif
BuildRequires:    gtkmm24-devel
BuildRequires:    libdnet-devel
BuildRequires:    libicu-devel
BuildRequires:    libmspack-devel
# Unfortunately, xmlsec1-openssl does not add libtool-ltdl
# dependency, so we need to add it ourselves.
BuildRequires:    libtool-ltdl-devel
BuildRequires:    libX11-devel
BuildRequires:    libXext-devel
BuildRequires:    libXi-devel
BuildRequires:    libXinerama-devel
BuildRequires:    libXrandr-devel
BuildRequires:    libXrender-devel
BuildRequires:    libXtst-devel
BuildRequires:    openssl-devel
BuildRequires:    pam-devel
BuildRequires:    procps-devel
BuildRequires:    systemd
BuildRequires:    xmlsec1-openssl-devel

Requires:         coreutils
Requires:         fuse
Requires:         net-tools
Requires:         grep
Requires:         pciutils
Requires:         sed
Requires:         systemd
Requires:         tar
Requires:         which
# xmlsec1-openssl needs to be added explicitly
Requires:         xmlsec1-openssl

# open-vm-tools >= 10.0.0 do not require open-vm-tools-deploypkg
# provided by VMware. That functionality is now available as part
# of open-vm-tools package itself.
Obsoletes:	  open-vm-tools-deploypkg <= 10.0.5

%description
The %{name} project is an open source implementation of VMware Tools. It
is a suite of open source virtualization utilities and drivers to improve the
functionality, user experience and administration of VMware virtual machines.
This package contains only the core user-space programs and libraries of
%{name}.

%package          desktop
Summary:          User experience components for Open Virtual Machine Tools
Group:            System Environment/Libraries
Requires:         %{name}%{?_isa} = %{version}-%{release}

%description      desktop
This package contains only the user-space programs and libraries of
%{name} that are essential for improved user experience of VMware virtual
machines.

%package          devel
Summary:          Development libraries for Open Virtual Machine Tools
Group:            Development/Libraries
Requires:         %{name}%{?_isa} = %{version}-%{release}

%description      devel
This package contains only the user-space programs and libraries of
%{name} that are essential for developing customized applications for
VMware virtual machines.

%prep
%setup -q -n %{name}-%{version}-%{toolsbuild}
%patch1 -p0

%build
# Required for regenerating configure script when
# configure.ac get modified
autoreconf -i
autoconf

%configure \
    --without-kernel-modules \
    --enable-xmlsec1 \
    --disable-static
sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool
make %{?_smp_mflags}

%install
export DONT_STRIP=1
make install DESTDIR=%{buildroot}

# Remove exec bit from config files
chmod a-x %{buildroot}%{_sysconfdir}/pam.d/*
chmod a-x %{buildroot}%{_sysconfdir}/vmware-tools/*.conf
chmod a-x %{buildroot}%{_sysconfdir}/vmware-tools/vgauth/schemas/*

# Remove exec bit on udev rules.
chmod a-x %{buildroot}%{_udevrulesdir}/99-vmware-scsi-udev.rules

# Remove the DOS line endings
sed -i "s|\r||g" README

# Remove "Encoding" key from the "Desktop Entry"
sed -i "s|^Encoding.*$||g" %{buildroot}%{_sysconfdir}/xdg/autostart/vmware-user.desktop

# Remove unnecessary files from packaging
find %{buildroot}%{_libdir} -name '*.la' -delete
rm -fr %{buildroot}%{_defaultdocdir}
rm -f docs/api/build/html/FreeSans.ttf

# Remove mount.vmhgfs & symlink
rm -fr %{buildroot}%{_sbindir} %{buildroot}/sbin/mount.vmhgfs

# Move vm-support to /usr/bin
mv %{buildroot}%{_sysconfdir}/vmware-tools/vm-support %{buildroot}%{_bindir}

# Systemd unit files
install -p -m 644 -D %{SOURCE1} %{buildroot}%{_unitdir}/%{toolsdaemon}.service
install -p -m 644 -D %{SOURCE2} %{buildroot}%{_unitdir}/%{vgauthdaemon}.service

# 'make check' in open-vm-tools rebuilds docs and ends up regenerating
# the font file. We can add %%check secion once 'make check' is fixed
# upstream

%post
if [ -f %{_bindir}/vmware-guestproxycerttool ]; then
   mkdir -p %{_sysconfdir}/vmware-tools/GuestProxyData/server
   mkdir -p -m 0700 %{_sysconfdir}/vmware-tools/GuestProxyData/trusted
   %{_bindir}/vmware-guestproxycerttool -g &> /dev/null || /bin/true
fi

# Setup mount point for Shared Folders
# NOTE: Use systemd-detect-virt to detect VMware platform because
#       vmware-checkvm might misbehave on non-VMware platforms.
if [ -f %{_bindir}/vmware-checkvm -a                     \
     -f %{_bindir}/vmhgfs-fuse ] &&                      \
   %{_bindir}/systemd-detect-virt | grep -iq VMware &&   \
   %{_bindir}/vmware-checkvm &> /dev/null &&             \
   %{_bindir}/vmware-checkvm -p | grep -q Workstation && \
   %{_bindir}/vmhgfs-fuse -e &> /dev/null; then
   mkdir -p /mnt/hgfs
fi

/sbin/ldconfig
%systemd_post %{vgauthdaemon}.service
%systemd_post %{toolsdaemon}.service

%preun
%systemd_preun %{toolsdaemon}.service
%systemd_preun %{vgauthdaemon}.service

if [ "$1" = "0" -a                                       \
     -f %{_bindir}/vmware-checkvm ] &&                   \
   %{_bindir}/systemd-detect-virt | grep -iq VMware &&   \
   %{_bindir}/vmware-checkvm &> /dev/null; then

   # Tell VMware that open-vm-tools is being uninstalled
   if [ -f %{_bindir}/vmware-rpctool ]; then
      %{_bindir}/vmware-rpctool 'tools.set.version 0' &> /dev/null || /bin/true
   fi

   # Teardown mount point for Shared Folders
   if [ -d /mnt/hgfs ] &&                               \
      %{_bindir}/vmware-checkvm -p | grep -q Workstation; then
      umount /mnt/hgfs &> /dev/null || /bin/true
      rmdir /mnt/hgfs &> /dev/null || /bin/true
   fi
fi

%postun
/sbin/ldconfig
%systemd_postun_with_restart %{toolsdaemon}.service
%systemd_postun_with_restart %{vgauthdaemon}.service
# Cleanup GuestProxy certs if open-vm-tools is being uninstalled
if [ "$1" = "0" ]; then
   rm -rf %{_sysconfdir}/vmware-tools/GuestProxyData &> /dev/null || /bin/true
fi

%post devel -p /sbin/ldconfig

%postun devel -p /sbin/ldconfig

%files
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc AUTHORS ChangeLog NEWS README
%config(noreplace) %{_sysconfdir}/pam.d/*
%dir %{_sysconfdir}/vmware-tools/
%dir %{_sysconfdir}/vmware-tools/vgauth
%dir %{_sysconfdir}/vmware-tools/vgauth/schemas
%config(noreplace) %{_sysconfdir}/vmware-tools/*.conf
# Don't expect users to modify VGAuth schema files
%config %{_sysconfdir}/vmware-tools/vgauth/schemas/*
%{_sysconfdir}/vmware-tools/*-vm-default
%{_sysconfdir}/vmware-tools/scripts
%{_sysconfdir}/vmware-tools/statechange.subr
%{_bindir}/VGAuthService
%{_bindir}/vm-support
%{_bindir}/vmhgfs-fuse
%{_bindir}/vmtoolsd
%{_bindir}/vmware-checkvm
%{_bindir}/vmware-guestproxycerttool
%{_bindir}/vmware-hgfsclient
%{_bindir}/vmware-namespace-cmd
%{_bindir}/vmware-rpctool
%{_bindir}/vmware-toolbox-cmd
%{_bindir}/vmware-vgauth-cmd
%{_bindir}/vmware-xferlogs
%{_libdir}/libDeployPkg.so.*
%{_libdir}/libguestlib.so.*
%{_libdir}/libhgfs.so.*
%{_libdir}/libvgauth.so.*
%{_libdir}/libvmtools.so.*
%dir %{_libdir}/%{name}/
%dir %{_libdir}/%{name}/plugins
%dir %{_libdir}/%{name}/plugins/common
%{_libdir}/%{name}/plugins/common/*.so
%dir %{_libdir}/%{name}/plugins/vmsvc
%{_libdir}/%{name}/plugins/vmsvc/*.so
%{_datadir}/%{name}/
%{_udevrulesdir}/99-vmware-scsi-udev.rules
%{_unitdir}/%{toolsdaemon}.service
%{_unitdir}/%{vgauthdaemon}.service

%files desktop
%{_sysconfdir}/xdg/autostart/*.desktop
%{_bindir}/vmware-user-suid-wrapper
%{_bindir}/vmware-vmblock-fuse
%{_libdir}/%{name}/plugins/vmusr/

%files devel
%doc docs/api/build/*
%exclude %{_includedir}/libDeployPkg/
%{_includedir}/vmGuestLib/
%{_libdir}/pkgconfig/*.pc
%{_libdir}/libDeployPkg.so
%{_libdir}/libguestlib.so
%{_libdir}/libhgfs.so
%{_libdir}/libvgauth.so
%{_libdir}/libvmtools.so

%changelog
* Thu Mar 16 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.1.5-3
- Need to add xmlsec1-openssl dependency explicitly.
  related: rhbz#1406901

* Tue Feb 28 2017 Richard W.M. Jones <rjones@redhat.com> - 10.1.5-2
- Use 0644 permissions for udev rules file.
  related: rhbz#1406901

* Tue Feb 28 2017 Richard W.M. Jones <rjones@redhat.com> - 10.1.5-1
- Rebase to open-vm-tools 10.1.5 from Fedora Rawhide
  resolves: rhbz#1406901
- Enable vgauthd.
  resolves: rhbz#1269243
- Add runtime dependency on pciutils (1388766).

* Thu Feb 02 2017 Richard W.M. Jones <rjones@redhat.com> - 10.0.5-4
- Fix failure to quiesce filesystem when Docker containers are running
  resolves: rhbz#1406483
- Fix for deadlock when taking a snapshot
  resolves: rhbz#1398802

* Mon Dec 12 2016 Richard W.M. Jones <rjones@redhat.com> - 10.0.5-3
- Increase SCSI timeouts with udev rule (RHBZ#1214347).

* Thu Jun 16 2016 Richard W.M. Jones <rjones@redhat.com> - 10.0.5-2
- Rebase to open-vm-tools 10.0.5 (from Fedora Rawhide)
  resolves: rhbz#1268537
- Remove PAM calls to pam_unix2.so module
  resolves: rhbz#1313071

* Tue May 3 2016 Dave Wysochanski <dwysocha@redaht.com> - 9.10.2-5
- Skip freezing autofs mounts.
  resolves: rhbz#1269956

* Fri Aug 14 2015 Richard W.M. Jones <rjones@redhat.com> - 9.10.2-4
- Enable PrivateTmp for additional hardening
  resolves: rhbz#1253698

* Wed Jul 29 2015 Richard W.M. Jones <rjones@redhat.com> - 9.10.2-3
- Enable deploypkg
  resolves: rhbz#1172335

* Mon Jul 27 2015 Richard W.M. Jones <rjones@redhat.com> - 9.10.2-2
- Disable vgauthd service in vmtoolsd.service file.
  resolves: rhbz#1172833

* Tue Jul 07 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 9.10.2-1
- Package new upstream version open-vm-tools-9.10.2-2822639
- Removed the patches that are no longer needed
  resolves: rhbz#1172833

* Wed May 20 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 9.10.0-2
- Claim ownership for /etc/vmware-tools directory
  resolves: rhbz#1223498

* Wed May 20 2015 Richard W.M. Jones <rjones@redhat.com> - 9.10.0-1
- Rebase to open-vm-tools 9.10.0 (synchronizing with F22)
  resolves: rhbz#1172833

* Fri Sep 19 2014 Richard W.M. Jones <rjones@redhat.com> - 9.4.0-6
- Really rebuild for updated procps
  resolves: rhbz#1140149

* Wed Sep 10 2014 Richard W.M. Jones <rjones@redhat.com> - 9.4.0-5
- Rebuild for updated procps
  resolves: rhbz#1140149

* Mon Aug 18 2014 Richard W.M. Jones <rjones@redhat.com> - 9.4.0-4
- Removed unnecessary package dependency on 'dbus'
- Moved 'vm-support' script to /usr/bin
- Added a call to 'tools.set.version' RPC to inform VMware
  platform when open-vm-tools has been uninstalled
- Add missing package dependency on 'which' (BZ#1045709)
- Add missing package dependencies (BZ#1045709, BZ#1077320)

* Tue Feb 11 2014 Richard W.M. Jones <rjones@redhat.com> - 9.4.0-3
- Only build on x86-64 for RHEL 7 (RHBZ#1054608).

* Wed Dec 04 2013 Richard W.M. Jones <rjones@redhat.com> - 9.4.0-2
- Rebuild for procps SONAME bump.

* Wed Nov 06 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.4.0-1
- Package new upstream version open-vm-tools-9.4.0-1280544.
- Added CUSTOM_PROCPS_NAME=procps and -Wno-deprecated-declarations
  for version 9.4.0.

* Thu Aug 22 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-11
- Added copyright and license text.
- Corrected summary for all packages. 

* Thu Aug 08 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-10
- Added options for hardening build (bug 990549). 
- Excluded unwanted file mount.vmhgfs from packaging (bug 990547).
- Removed deprecated key "Encoding" from "Desktop Entry" (bug 990552).

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 9.2.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun  4 2013 Richard W.M. Jones <rjones@redhat.com> - 9.2.3-8
- RHEL 7 now includes libdnet, so re-enable it.

* Fri May 24 2013 Richard W.M. Jones <rjones@redhat.com> - 9.2.3-6
- +BR gcc-c++.  If this is missing it fails to build.
- On RHEL, disable libdnet.

* Mon May 06 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-5
- Renamed source file open-vm-tools.service -> vmtoolsd.service
  to match it with the service name.

* Wed May 01 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-4
- Bumped the release to pick the new service definition with
  no restart directive.

* Mon Apr 29 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-3
- open-vm-tools-9.2.3 require glib-2.14.0.

* Mon Apr 29 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-2
- Bumped the release to pick the new service definition.

* Thu Apr 25 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-1
- Package new upstream version open-vm-tools-9.2.3-1031360.
- Removed configure options CUSTOM_PROCPS_NAME (for libproc) and
  -Wno-deprecated-declarations as these have been addressed in
  open-vm-tools-9.2.3-1031360.

* Wed Apr 24 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-12
- Removed %%defattr and BuildRoot.
- Added ExclusiveArch.
- Replaced /usr/sbin/ldconfig with /sbin/ldconfig.

* Mon Apr 22 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-11
- Removed the conditional steps for old versions of Fedora and RHEL.

* Thu Apr 18 2013 Ravindra Kumar <ravindrakumar at vmware.com> - 9.2.2-10
- Addressed formal review comments from Simone Caronni.
- Removed %%check section because 'make check' brings font file back.

* Wed Apr 17 2013 Simone Caronni <negativo17@gmail.com> - 9.2.2-9
- Removed rm command in %%check section.
- Remove blank character at the beginning of each changelog line.

* Mon Apr 15 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-8
- Removed FreeSans.ttf font file from packaging.
- Added 'rm' command to remove font file in %%check section because
  'make check' adds it back.
- Added doxygen dependency back.

* Thu Apr 11 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-7
- Applied patch from Simone for removal of --docdir option from configure.
- Removed unnecessary --enable-docs option from configure.
- Removed doxygen dependency.

* Thu Apr 11 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-6
- Replaced vmtoolsd with a variable.
- Changed summary for subpackages to be more specific.
- Removed drivers.txt file as we don't really need it.
- Fixed vmGuestLib ownership for devel package.
- Removed systemd-sysv from Requires for Fedora 18+ and RHEL 7+.
- Made all "if" conditions consistent.

* Wed Apr 10 2013 Simone Caronni <negativo17@gmail.com> - 9.2.2-5
- Added RHEL 5/6 init script.
- Renamed SysV init script / systemd service file to vmtoolsd.
- Fixed ownership of files from review.
- Moved api documentation in devel subpackage.
- Removed static libraries.

* Tue Apr 09 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-4
- Applied part of review fixes patch from Simone Caronni for systemd setup.
- Replaced tabs with spaces all over.

* Tue Apr 09 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-3
- Applied review fixes patch from Simone Caronni.
- Added missing *.a and *.so files for devel package.
- Removed unnecessary *.la plugin files from base package.

* Mon Apr 08 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-2
- Modified SPEC to follow the conventions and guidelines.
- Addressed review comments from Mohamed El Morabity.
- Added systemd script.
- Verified and built the RPMS for Fedora 18.
- Fixed rpmlint warnings.
- Split the UX components in a separate package for desktops.
- Split the help files in a separate package for help.
- Split the guestlib headers in a separate devel package.

* Mon Jan 28 2013 Sankar Tanguturi <stanguturi@vmware.com> - 9.2.2-1
- Initial SPEC file to build open-vm-tools for Fedora 17.
