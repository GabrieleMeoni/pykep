/*****************************************************************************
 *   Copyright (C) 2004-2018 The pykep development team,                     *
 *   Advanced Concepts Team (ACT), European Space Agency (ESA)               *
 *                                                                           *
 *   https://gitter.im/esa/pykep                                             *
 *   https://github.com/esa/pykep                                            *
 *                                                                           *
 *   act@esa.int                                                             *
 *                                                                           *
 *   This program is free software; you can redistribute it and/or modify    *
 *   it under the terms of the GNU General Public License as published by    *
 *   the Free Software Foundation; either version 2 of the License, or       *
 *   (at your option) any later version.                                     *
 *                                                                           *
 *   This program is distributed in the hope that it will be useful,         *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of          *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           *
 *   GNU General Public License for more details.                            *
 *                                                                           *
 *   You should have received a copy of the GNU General Public License       *
 *   along with this program; if not, write to the                           *
 *   Free Software Foundation, Inc.,                                         *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.               *
 *****************************************************************************/

#ifndef KEP_TOOLBOX_SPICE_UTILS_H
#define KEP_TOOLBOX_SPICE_UTILS_H

#include <sstream>
#include <string>

#include "../astro_constants.h"
#include "../epoch.h"
#include "../exceptions.h"
#include "../third_party/cspice/SpiceUsr.h"
#include "../third_party/cspice/SpiceZfc.h"
#include "../third_party/cspice/SpiceZmc.h"

namespace kep_toolbox
{
namespace util
{

__KEP_TOOL_VISIBLE void load_spice_kernel(std::string file_name);
__KEP_TOOL_VISIBLE SpiceDouble epoch_to_spice(kep_toolbox::epoch ep);
__KEP_TOOL_VISIBLE SpiceDouble epoch_to_spice(double mjd2000);
}
} // namespaces
#endif // KEP_TOOLBOX_SPICE_UTILS_H
