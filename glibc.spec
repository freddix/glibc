# based on PLD Linux spec git://git.pld-linux.org/packages/glibc.git
# includes locale-gen script from Arch Linux

%if "%{_target_base_arch}" != "%{_host_base_arch}"
%define		with_cross  1
%define		no_install_post_chrpath    1
%endif

%undefine	with_cross

Summary:	GNU libc
Name:		glibc
Version:	2.21
Release:	2
Epoch:		6
License:	LGPL v2.1+
Group:		Libraries
Source0:	http://ftp.gnu.org/pub/gnu/glibc/%{name}-%{version}.tar.xz
# Source0-md5:	9cb398828e8f84f57d1f7d5588cf40cd
Source1:	localedb-gen
Source2:	%{name}-LD-path.c
Source3:	nsswitch.conf
Source4:	localedb-gen
Source5:	localedb-gen.txt
#
Patch0:		%{name}-paths.patch
Patch1:		%{name}-branch.patch
URL:		http://www.gnu.org/software/libc/
BuildRequires:	autoconf
BuildRequires:	binutils
BuildRequires:	gawk
BuildRequires:	gcc
BuildRequires:	gettext
BuildRequires:	glibc-static
BuildRequires:	linux-libc-headers
BuildRequires:	perl-base
BuildRequires:	rpm-build
BuildRequires:	rpm-perlprov
BuildRequires:	sed
BuildRequires:	texinfo
Requires(post):	ldconfig = %{epoch}:%{version}-%{release}
Provides:	glibc(nptl)
Provides:	glibc(tls)
Provides:	rtld(GNU_HASH)
Obsoletes:	glibc-misc
Suggests:	localedb-src
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# avoid -s here (ld.so must not be stripped to allow any program debugging)
%define		filterout_ld		(-Wl,)?-[sS] (-Wl,)?--strip.*

# avoid -D_FORTIFY_SOURCE=X
%define		filterout_cpp	-D_FORTIFY_SOURCE=[0-9]+

# switch off debug
%define		specflags	-DNDEBUG

# ld.so needs not to be stripped to work
# gdb needs unstripped libpthread for some threading support
# ...but we can strip at least debuginfo from them
%define		_autostripdebug		.*/ld-[0-9.]*so\\|.*/libpthread-[0-9.]*so\\|.*libthread_db-[0-9.]*so

# we don't want perl dependency in glibc-devel
%define		_noautoreqfiles		%{_bindir}/mtrace
# hack: don't depend on rpmlib(PartialHardlinkSets) for easier upgrade from Ra
# (hardlinks here are unlikely to be "partial"... and rpm 4.0.2 from Ra was
# patched not to crash on partial hardlinks too)
%define		_hack_dontneed_PartialHardlinkSets	1
%define		_noautochrpath		.*\\(ldconfig\\|sln\\)

# private symbols
%define		_noautoprov		.*\(GLIBC_PRIVATE\)
%define		_noautoreq		.*\(GLIBC_PRIVATE\)

%description
Contains the standard libraries that are used by multiple programs on
the system. In order to save disk space and memory, as well as to ease
upgrades, common system code is kept in one place and shared between
programs. This package contains the most important sets of shared
libraries, the standard C library and the standard math library.
Without these, a Linux system will not function. It also contains
national language (locale) support.

%package devel
Summary:	Additional libraries required to compile
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	%{name}-devel-utils = %{epoch}:%{version}-%{release}
Requires:	%{name}-headers = %{epoch}:%{version}-%{release}
Provides:	%{name}-devel(%{_target_cpu}) = %{epoch}:%{version}-%{release}
Obsoletes:	libiconv-devel

%description devel
To develop programs which use the standard C libraries (which nearly
all programs do), the system needs to have these standard header files
and object files available for creating the executables.

%package -n ldconfig
Summary:	Create shared library cache and maintains symlinks
Group:		Applications/System
# This is needed because previous package (glibc) had autoreq false and had
# provided this manually. Probably poldek bug that have to have it here.
Provides:	/sbin/ldconfig

%description -n ldconfig
ldconfig scans a running system and sets up the symbolic links that
are used to load shared libraries properly. It also creates
/etc/ld.so.cache which speeds the loading programs which use shared
libraries.

%package headers
Summary:	Header files for development using standard C libraries
Group:		Development/Building
Provides:	%{name}-headers(%{_target_cpu}) = %{epoch}:%{version}-%{release}
%if "%{_lib}" == "lib64"
Provides:	%{name}-headers(64bit) = %{epoch}:%{version}-%{release}
%endif
%ifarch %{x8664}
# If both -m32 and -m64 is to be supported on x86_64, x86_64 package
# have to be installed, not ix86 one.
Obsoletes:	glibc-headers(i686)
%endif
Requires:	linux-libc-headers

%description headers
The glibc-headers package contains the header files necessary for
developing programs which use the standard C libraries (which are used
by nearly all programs). If you are developing programs which will use
the standard C libraries, your system needs to have these standard
header files available in order to create the executables.

Install glibc-headers if you are going to develop programs which will
use the standard C libraries.

%package devel-utils
Summary:	Utilities needed for development using standard C libraries
Group:		Development/Libraries
Provides:	%{name}-devel-utils(%{_target_cpu}) = %{epoch}:%{version}-%{release}
%ifarch %{x8664}
# If both -m32 and -m64 is to be supported on AMD64, x86_64 package
# have to be installed, not ix86 one.
Obsoletes:	glibc-devel-utils(i686)
%endif

%description devel-utils
The glibc-devel-utils package contains utilities necessary for
developing programs which use the standard C libraries (which are used
by nearly all programs). If you are developing programs which will use
the standard C libraries, your system needs to have these utilities
available.

Install glibc-devel-utils if you are going to develop programs which
will use the standard C libraries.

%package devel-doc
Summary:	Documentation needed for development using standard C libraries
Group:		Documentation
Provides:	%{name}-devel-doc(%{_target_cpu}) = %{epoch}:%{version}-%{release}
%ifarch %{x8664}
# If both -m32 and -m64 is to be supported on x86_64, x86_64 package
# have to be installed, not ix86 one.
Obsoletes:	glibc-devel-doc(i686)
%endif
%description devel-doc
The glibc-devel-doc package contains info and manual pages necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).

Install glibc-devel-doc if you are going to develop programs which
will use the standard C libraries.

%package -n localedb-src
Summary:	locale database source code
Group:		Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	gzip
Requires:	sed

%description -n localedb-src
This add-on package contains the data needed to build the locale data
files to use the internationalization features of the GNU libc.

%package -n iconv
Summary:	Convert encoding of given files from one encoding to another
Group:		Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n iconv
Convert encoding of given files from one encoding to another. You need
this package if you want to convert some document from one encoding to
another or if you have installed some programs which use Generic
Character Set Conversion Interface.

%package static
Summary:	Static libraries
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}
Provides:	%{name}-static(%{_target_cpu}) = %{epoch}:%{version}-%{release}
Obsoletes:	libiconv-static

%description static
GNU libc static libraries.

%package -n nss_db
Summary:	DB NSS glibc module
Group:		Base
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n nss_db
DB NSS glibc module.

%package -n nss_compat
Summary:	Old style NYS NSS glibc module
Group:		Base
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n nss_compat
Old style NYS NSS glibc module.

%package -n nss_dns
Summary:	BIND NSS glibc module
Group:		Base
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n nss_dns
BIND NSS glibc module.

%package -n nss_files
Summary:	Traditional files databases NSS glibc module
Group:		Base
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n nss_files
Traditional files databases NSS glibc module.

%package -n nss_hesiod
Summary:	hesiod NSS glibc module
Group:		Base
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n nss_hesiod
glibc NSS (Name Service Switch) module for databases access.

%package -n nss_nis
Summary:	NIS(YP) NSS glibc module
Group:		Base
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n nss_nis
glibc NSS (Name Service Switch) module for NIS(YP) databases access.

%package -n nss_nisplus
Summary:	NIS+ NSS module
Group:		Base
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n nss_nisplus
glibc NSS (Name Service Switch) module for NIS+ databases access.

%package pic
Summary:	glibc PIC archive
Group:		Development/Libraries/Libc
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}

%description pic
GNU C Library PIC archive contains an archive library (ar file)
composed of individual shared objects. This is used for creating a
library which is a smaller subset of the standard libc shared library.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%ifarch %{ix86}
# no need to search for libs in /usr/{lib32x,lib64} on x86
%{__sed} -i "s#add_system_dir#do_not_add_system_dir#" sysdeps/unix/sysv/linux/x86_64/dl-cache.h
%endif

chmod +x scripts/cpp

%build
rm -rf builddir
install -d builddir
cd builddir

cat >> configparms << EOF
localedir=%{_prefix}/lib/locale
slibdir=%{_libdir}
rtlddir=%{_libdir}
sbindir=%{_sbindir}
rootsbindir=%{_sbindir}
EOF

%if %{with cross}
../configure \
	libc_cv_c_cleanup=yes		\
	libc_cv_ctors_header=yes	\
	libc_cv_forced_unwind=yes	\
	CFLAGS="%{rpmcflags}"		\
	LDFLAGS="%{rpmldflags}"		\
	--build=%{_build}		\
	--host="%{_target_cpu}-freddix-linux"	\
	--prefix=%{_prefix}		\
	--bindir=%{_bindir}		\
	--infodir=%{_infodir}		\
	--libdir=%{_libdir}		\
	--libexecdir=%{_libexecdir}	\
	--mandir=%{_mandir}		\
	--sbindir=%{_sbindir}		\
%else
../%configure \
	--enable-add-ons		\
	--enable-bind-now		\
	--enable-lock-elision		\
	--enable-multi-arch		\
	--enable-obsolete-rpc		\
%endif
	--disable-profile		\
	--disable-werror		\
	--enable-kernel=2.6.32		\
	--with-headers=%{_includedir}	\
	--without-cvs			\
	--without-selinux
%{__make}
cd ..

%if %{without cross}
%{__cc} %{SOURCE2} %{rpmcflags} -Os -static -o glibc-postinst
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_prefix}/lib/locale,/var/log,/var/cache/ldconfig}

cd builddir
%{__make} install \
	install_root=$RPM_BUILD_ROOT \
	infodir=%{_infodir} \
	mandir=%{_mandir}

# Include %{_libdir}/gconv/gconv-modules.cache
./elf/ld.so \
    --inhibit-cache \
    --library-path . \
    ./iconv/iconvconfig \
    --nostdlib %{_libdir}/gconv \
    --prefix=$RPM_BUILD_ROOT \
    -o $RPM_BUILD_ROOT%{_libdir}/gconv/gconv-modules.cache
cd ..

%if %{without cross}
install glibc-postinst $RPM_BUILD_ROOT%{_sbindir}
%endif
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/nsswitch.conf
install posix/gai.conf $RPM_BUILD_ROOT%{_sysconfdir}

: > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.cache
install -d $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d
echo 'include ld.so.conf.d/*.conf' > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf
: > $RPM_BUILD_ROOT/var/cache/ldconfig/aux-cache

# localedb-gen infrastructure
sed -e 's,@localedir@,%{_prefix}/lib/locale,' %{SOURCE4} > $RPM_BUILD_ROOT%{_bindir}/localedb-gen
chmod +x $RPM_BUILD_ROOT%{_bindir}/localedb-gen
install %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/localedb.gen
%{__sed} -e '1,3d' -e 's|/| |g' -e 's|\\| |g' -e 's|^|#|g' \
    localedata/SUPPORTED >> $RPM_BUILD_ROOT%{_sysconfdir}/localedb.gen

# make symlinks across top-level directories absolute
for l in BrokenLocale anl cidn crypt dl m nsl resolv rt thread_db util; do
    # test -L $RPM_BUILD_ROOT%{_libdir}/lib${l}.so || exit 1
    rm -f $RPM_BUILD_ROOT%{_libdir}/lib${l}.so
    ln -sf $(basename $RPM_BUILD_ROOT%{_libdir}/lib${l}.so.*) $RPM_BUILD_ROOT%{_libdir}/lib${l}.so
done

# additional documentation, don't use __rm macro here
rm -rf documentation
install -d documentation
for f in DESIGN-{barrier,condvar,rwlock}.txt TODO{,-kernel,-testing}; do
	cp -af nptl/$f documentation/$f.nptl
done
cp -af crypt/README.ufc-crypt ChangeLog* documentation

# Collect locale files and mark them with %%lang()
echo '%defattr(644,root,root,755)' > glibc.lang
for i in $RPM_BUILD_ROOT%{_localedir}/*; do
	if [ -d $i ]; then
		lang=$(basename $i)
		dir="${i#$RPM_BUILD_ROOT}"
		echo "%lang($lang) $dir" >> glibc.lang
	fi
done

# post-install clean up
%{__rm} $RPM_BUILD_ROOT%{_infodir}/dir
# remove the static libraries that have a shared counterpart
# libc, libdl, libm and libpthread are required for toolchain testsuites
# in addition libcrypt appears widely required
%{__rm} $RPM_BUILD_ROOT%{_libdir}/lib{anl,BrokenLocale,nsl,resolv,rt,util}.a
# doesn't fit with out tzdata concept and configure.in is stupid assuming bash
# is first posix compatible shell making this script depend on bash.
%{__rm} $RPM_BUILD_ROOT%{_bindir}/tzselect

# NOTES:
# Languages not supported by glibc locales, but usable via $LANGUAGE:
#   ang - Old English (gtk+, gnome)
#   ca@valencia (gtk+, gnome; as ca_ES@valencia in FileZilla; locale exists in Debian)
#   en@shaw - English with Shavian alphabet (gnome)
#   la - Latin
#   tlh - Klingon (bzflag)
#
# To be added when they become supported by glibc:
#   ach (vlc)
#   ak (gtkspell3)
#   bal (newt,pessulus)
#   cgg (vlc)
#   co  (vlc)
#   frp (xfce, lxlauncher)
#   gn  (gn_BR in gnome, maybe gn_PY)
#   haw (iso-codes, stellarium)
#   hrx (stellarium)
#   ilo (kudzu)
#   io  (gtk+2, gnome, alacarte)
#   jv  (gmpc, avant-window-navigator, kdesudo)
#   kmr (vlc)
#   man (ccsm; incorrectly named md)
#   mus (bluez-gnome)
#   pms (deluge)
#   sco (gnomad2, picard, stellarium)
#   son (gtkspell3)
#   swg (sim)
#   syr (iso-codes)
#   tet (vlc)
#   vec (mate-applet-indicator)
#
# To be removed (after fixing packages still using it):
#   sr@Latn (use sr@latin instead)
#   sr@ije (use sr@ijekavian instead)
#
# Short forms (omitted country code, used instead of long form) for ambiguous or unclear cases:
# aa=aa_ER
# ar=common? (AE, BH, DZ, EG, IQ, JO, KW, LB, LY, MA, OM, QA, SA, SD, SY, TN, YE)
# az=az_AZ
# bn=bn_BD
# bo=bo_CN? (or common for CN, IN?)
# ca=ca_ES
# ckb=ckb_IQ
# cv=cv_RU
# de=de_DE
# en=common? (en_AU, en_CA, en_GB, en_NZ, en_US are used for particular variants)
# eo=common
# es=es_ES
# eu=eu_ES
# fa=fa_IR
# ff=ff_SN
# fr=fr_FR
# fy=fy_NL
# gez=gez_ET (?)
# it=it_IT
# li=li_NL
# nds=nds_DE
# nl=nl_NL
# om=om_ET
# or=or_IN
# pa=pa_IN
# pt=pt_PT
# ru=ru_RU
# sd=sd_IN
# so=so_SO
# sr=sr_RS [cyrillic]
# sr@latin=sr_RS@latin
# sr@ijekavian=sr_BA@ijekavian
# sr@ijekavianlatin=sr_BA@ijekavianlatin
# sv=sv_SE
# sw=sw_TZ (or common for KE, TZ, UG?)
# ta=ta_IN
# te=te_IN
# ti=ti_ER (?)
# tr=tr_TR
# ur=ur_PK (?)
# zh: no short code used (use zh_CN, zh_HK, zh_SG[not included yet], zh_TW)
#
# Omitted here - already existing (with libc.mo):
#   be ca cs da de el en_GB es fi fr gl hr hu it ja ko nb nl pl pt_BR ru rw sk
#   sv tr zh_CN zh_TW
#
for i in aa aa@saaho af am an ang ar ar_TN as ast az az_IR be@latin be@tarask bem \
	bg bn bn_IN bo br bs byn ca@valencia ckb cmn crh csb cv cy de_AT de_CH dv dz en \
	en@boldquot en@quot en@shaw en_AU en_CA en_NZ en_US eo es_AR es_CL es_CO es_CR \
	es_DO es_EC es_GT es_HN es_MX es_NI es_PA es_PE es_PR es_SV es_UY \
	es_VE et eu fa ff fil fo fr_BE fr_CA fr_CH fur fy ga gd gez gu gv ha he \
	hi hne hsb hy ia id ig ik is it_CH iu ka kg kk kl km kn kok ks ku kw ky la lb \
	lg li lo lt lv mai mg mhr mi mk ml mn mr ms mt my nds ne nl_BE nn nr nso \
	oc om or pa pap ps pt ps rm ro sa sc sd se si sid sl so sq sr sr@Latn tl \
	sr@ije sr@ijekavian sr@ijekavianlatin sr@latin ss st sw ta te tg th ti \
	tig tk tl tlh tn ts tt tt@iqtelif ug uk ur uz uz@cyrillic ve vi wa wal wo xh yi yo \
	zh_HK zu; do
	if [ ! -d $RPM_BUILD_ROOT%{_localedir}/$i/LC_MESSAGES ]; then
		install -d $RPM_BUILD_ROOT%{_localedir}/$i/LC_MESSAGES
		# use lang() tags with ll_CC@variant (stripping charset and @quot|@boldquot)
		lang=$(echo $i | sed -e 's/@quot\>\|@boldquot\>//')
		echo "%lang($lang) %{_localedir}/$i" >> glibc.lang
	fi
done

# LC_TIME category, used for localized date formats (at least by coreutils)
for i in af be bg ca cs da de el en eo es et eu fi fr ga gl hr hu ia id it ja kk ko lg lt \
	ms nb nl pl pt pt_BR ro ru rw sk sl sv tr uk vi zh_CN zh_TW; do
	if [ ! -d $RPM_BUILD_ROOT%{_localedir}/$i ]; then
		echo "%lang($lang) %{_localedir}/$i" >> glibc.lang
	fi
	install -d $RPM_BUILD_ROOT%{_localedir}/$i/LC_TIME
done

%if 0
%check
cd builddir
%{__make} -j1 check
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{without cross}
%post	-p /usr/sbin/postshell
/usr/sbin/glibc-postinst %{_libdir}/%{_host_cpu} %{_libdir}/tls
/usr/sbin/ldconfig
%else
%post -p /usr/sbin/ldconfig
%endif

%postun -p /usr/sbin/ldconfig

%post -n iconv -p %{_sbindir}/iconvconfig

%post -n localedb-src
localedb-gen ||:

%post devel -p /usr/sbin/postshell
-/usr/sbin/fix-info-dir -c %{_infodir}

%postun	devel -p /usr/sbin/postshell
-/usr/sbin/fix-info-dir -c %{_infodir}

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README NEWS BUGS
%attr(755,root,root) %{_bindir}/catchsegv
%attr(755,root,root) %{_bindir}/getconf
%attr(755,root,root) %{_bindir}/getent
%attr(755,root,root) %{_bindir}/iconv
%attr(755,root,root) %{_bindir}/ldd
%attr(755,root,root) %{_bindir}/pldd
%attr(755,root,root) %{_bindir}/locale
%attr(755,root,root) %{_bindir}/rpcgen
%attr(755,root,root) %{_sbindir}/sln
%attr(755,root,root) %{_sbindir}/zdump
%attr(755,root,root) %{_sbindir}/zic
%if %{without cross}
%attr(755,root,root) %{_sbindir}/glibc-postinst
%endif
%ifarch %{x8664}
%attr(755,root,root) %{_libdir}/ld-linux-x86-64.so.2
%endif
%ifarch %{ix86}
%attr(755,root,root) %{_bindir}/lddlibc4
%attr(755,root,root) %{_libdir}/ld-linux.so.2
%endif
%attr(755,root,root) %{_libdir}/ld-2.21.so
%attr(755,root,root) %{_libdir}/libBrokenLocale-*.so
%attr(755,root,root) %{_libdir}/libBrokenLocale.so.1
%attr(755,root,root) %{_libdir}/libSegFault.so
%attr(755,root,root) %{_libdir}/libanl-*.so
%attr(755,root,root) %{_libdir}/libanl.so.1
%attr(755,root,root) %{_libdir}/libc-*.so
%attr(755,root,root) %{_libdir}/libc.so.6
%attr(755,root,root) %{_libdir}/libcidn-*.so
%attr(755,root,root) %{_libdir}/libcidn.so.1
%attr(755,root,root) %{_libdir}/libcrypt-*.so
%attr(755,root,root) %{_libdir}/libcrypt.so.1
%attr(755,root,root) %{_libdir}/libdl-*.so
%attr(755,root,root) %{_libdir}/libdl.so.2
%attr(755,root,root) %{_libdir}/libm-*.so
%attr(755,root,root) %{_libdir}/libm.so.6
%attr(755,root,root) %{_libdir}/libnsl-*.so
%attr(755,root,root) %{_libdir}/libnsl.so.1
%attr(755,root,root) %{_libdir}/libnss_dns-*.so
%attr(755,root,root) %{_libdir}/libnss_dns.so.2
%attr(755,root,root) %{_libdir}/libnss_files-*.so
%attr(755,root,root) %{_libdir}/libnss_files.so.2
%attr(755,root,root) %{_libdir}/libpthread-*.so
%attr(755,root,root) %{_libdir}/libpthread.so.0
%attr(755,root,root) %{_libdir}/libresolv-*.so
%attr(755,root,root) %{_libdir}/libresolv.so.2
%attr(755,root,root) %{_libdir}/librt-*.so
%attr(755,root,root) %{_libdir}/librt.so.1
%attr(755,root,root) %{_libdir}/libthread_db-1.0.so
%attr(755,root,root) %{_libdir}/libthread_db.so.1
%attr(755,root,root) %{_libdir}/libutil-*.so
%attr(755,root,root) %{_libdir}/libutil.so.1

%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nsswitch.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gai.conf

%config %{_sysconfdir}/rpc

%dir %{_libexecdir}
%dir %{_libexecdir}/getconf
%attr(755,root,root) %{_libexecdir}/getconf/*

%dir %{_datadir}/locale
%{_datadir}/locale/locale.alias

%files -n ldconfig
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/ldconfig
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ld.so.conf
%dir %attr(700,root,root) /var/cache/ldconfig
%dir %{_sysconfdir}/ld.so.conf.d
%ghost %attr(600,root,root) /var/cache/ldconfig/aux-cache
%ghost %{_sysconfdir}/ld.so.cache

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libBrokenLocale.so
%attr(755,root,root) %{_libdir}/libanl.so
%attr(755,root,root) %{_libdir}/libcrypt.so
%attr(755,root,root) %{_libdir}/libcidn.so
%attr(755,root,root) %{_libdir}/libdl.so
%attr(755,root,root) %{_libdir}/libm.so
%attr(755,root,root) %{_libdir}/libnsl.so
%attr(755,root,root) %{_libdir}/libpcprofile.so
%attr(755,root,root) %{_libdir}/libresolv.so
%attr(755,root,root) %{_libdir}/librt.so
%attr(755,root,root) %{_libdir}/libthread_db.so
%attr(755,root,root) %{_libdir}/libutil.so
%{_libdir}/crt[1in].o
%{_libdir}/[MSg]crt1.o
# ld scripts
%{_libdir}/libc.so
%{_libdir}/libpthread.so
# static-only libs
%{_libdir}/libc_nonshared.a
%{_libdir}/libg.a
%{_libdir}/libieee.a
%{_libdir}/libpthread_nonshared.a
%{_libdir}/librpcsvc.a
%{_includedir}/gnu/stubs-*.h

%files headers
%defattr(644,root,root,755)
%{_includedir}/*.h
%{_includedir}/arpa
%{_includedir}/bits
%dir %{_includedir}/gnu
%{_includedir}/gnu/lib*.h
%{_includedir}/gnu/stubs.h
%{_includedir}/net
%{_includedir}/netash
%{_includedir}/netatalk
%{_includedir}/netax25
%{_includedir}/neteconet
%{_includedir}/netiucv
%{_includedir}/netinet
%{_includedir}/netipx
%{_includedir}/netpacket
%{_includedir}/netrom
%{_includedir}/netrose
%{_includedir}/nfs
%{_includedir}/protocols
%{_includedir}/rpc
%{_includedir}/rpcsvc
%{_includedir}/scsi
%{_includedir}/sys

%files devel-utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/gencat
%attr(755,root,root) %{_bindir}/*prof*
%attr(755,root,root) %{_bindir}/*trace

%files devel-doc
%defattr(644,root,root,755)
%doc documentation/* PROJECTS
%{_infodir}/libc.info*

%files -n localedb-src
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/localedef
%attr(755,root,root) %{_bindir}/localedb-gen
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/localedb.gen
%dir %{_prefix}/lib/locale
%{_datadir}/i18n

%files -n iconv
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/iconvconfig
%dir %{_libdir}/gconv
%{_libdir}/gconv/gconv-modules
%verify(not md5 mtime size) %{_libdir}/gconv/gconv-modules.cache
%attr(755,root,root) %{_libdir}/gconv/*.so

%files static
%defattr(644,root,root,755)
%{_libdir}/libc.a
%{_libdir}/libcrypt.a
%{_libdir}/libdl.a
%{_libdir}/libm.a
%{_libdir}/libmcheck.a
%{_libdir}/libpthread.a

%files -n nss_db
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/makedb
%attr(755,root,root) %{_libdir}/libnss_db-*.so
%attr(755,root,root) %{_libdir}/libnss_db.so.2
%{_var}/db/Makefile

%files -n nss_compat
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libnss_compat-*.so
%attr(755,root,root) %{_libdir}/libnss_compat.so.2

%files -n nss_hesiod
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libnss_hesiod-*.so
%attr(755,root,root) %{_libdir}/libnss_hesiod.so.2

%files -n nss_nis
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libnss_nis-*.so
%attr(755,root,root) %{_libdir}/libnss_nis.so.2

%files -n nss_nisplus
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libnss_nisplus-*.so
%attr(755,root,root) %{_libdir}/libnss_nisplus.so.2

