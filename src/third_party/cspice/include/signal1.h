/*

-Header_File signal1.h (CSPICE version of the f2c signal1.h header file)

-Abstract

   Define macros associated with signal handling, customized for the
   host environment.

-Disclaimer

   THIS SOFTWARE AND ANY RELATED MATERIALS WERE CREATED BY THE
   CALIFORNIA INSTITUTE OF TECHNOLOGY (CALTECH) UNDER A U.S.
   GOVERNMENT CONTRACT WITH THE NATIONAL AERONAUTICS AND SPACE
   ADMINISTRATION (NASA). THE SOFTWARE IS TECHNOLOGY AND SOFTWARE
   PUBLICLY AVAILABLE UNDER U.S. EXPORT LAWS AND IS PROVIDED "AS-IS"
   TO THE RECIPIENT WITHOUT WARRANTY OF ANY KIND, INCLUDING ANY
   WARRANTIES OF PERFORMANCE OR MERCHANTABILITY OR FITNESS FOR A
   PARTICULAR USE OR PURPOSE (AS SET FORTH IN UNITED STATES UCC
   SECTIONS 2312-2313) OR FOR ANY PURPOSE WHATSOEVER, FOR THE
   SOFTWARE AND RELATED MATERIALS, HOWEVER USED.

   IN NO EVENT SHALL CALTECH, ITS JET PROPULSION LABORATORY, OR NASA
   BE LIABLE FOR ANY DAMAGES AND/OR COSTS, INCLUDING, BUT NOT
   LIMITED TO, INCIDENTAL OR CONSEQUENTIAL DAMAGES OF ANY KIND,
   INCLUDING ECONOMIC DAMAGE OR INJURY TO PROPERTY AND LOST PROFITS,
   REGARDLESS OF WHETHER CALTECH, JPL, OR NASA BE ADVISED, HAVE
   REASON TO KNOW, OR, IN FACT, SHALL KNOW OF THE POSSIBILITY.

   RECIPIENT BEARS ALL RISK RELATING TO QUALITY AND PERFORMANCE OF
   THE SOFTWARE AND ANY RELATED MATERIALS, AND AGREES TO INDEMNIFY
   CALTECH AND NASA FOR ALL THIRD-PARTY CLAIMS RESULTING FROM THE
   ACTIONS OF RECIPIENT IN THE USE OF THE SOFTWARE.

-Required_Reading

   None.

-Particulars

   This header defines the macro signal1 referenced in main.c,
   which is a generic main routine used in CSPICE executables that
   link to code generated by f2c.

-Literature_References

   None.

-Author_and_Institution

   N.J. Bachman       (JPL)

-Restrictions

  1) This header file must be updated whenever the f2c processor
     or the f2c libraries libI77 and libF77 are updated.

  2) This header may need to be updated to support new platforms.
     The supported platforms at the time of the 03-FEB-2000 release
     are:

        ALPHA-DIGITAL-UNIX_C
        HP_C
        NEXT_C
        PC-LINUX_C
        PC-MS_C
        SGI-IRIX-N32_C
        SGI-IRIX-NO2_C
        SUN-SOLARIS-GCC_C
        SUN-SOLARIS-NATIVE_C

-Version

   -CSPICE Version 1.0.0, 03-FEB-2000 (NJB)

*/

/* You may need to adjust the definition of signal1 to supply a */
/* cast to the correct argument type.  This detail is system- and */
/* compiler-dependent.   The #define below assumes signal.h declares */
/* type SIG_PF for the signal function's second argument. */

#include <signal.h>

#ifndef Sigret_t
#define Sigret_t void
#endif
#ifndef Sigarg_t
#ifdef KR_headers
#define Sigarg_t
#else
#ifdef __cplusplus
#define Sigarg_t ...
#else
#define Sigarg_t int
#endif
#endif
#endif /*Sigarg_t*/

#ifdef USE_SIG_PF /* compile with -DUSE_SIG_PF under IRIX */
#define sig_pf SIG_PF
#else
typedef Sigret_t (*sig_pf)(Sigarg_t);
#endif

#define signal1(a, b) signal(a, (sig_pf)b)

#ifdef __cplusplus
#define Sigarg ...
#define Use_Sigarg
#else
#define Sigarg Int n
#define Use_Sigarg n = n /* shut up compiler warning */
#endif
