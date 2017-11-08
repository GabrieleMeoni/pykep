import PyKEP as pk
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class _indirect_base(object):
    """Base class for indirect trajectory optimisation problems.

    All inheriting classes will adopt ``plot_traj`` and ``plot_control`` and ``pretty`` and ``get_traj`` and have
    to implement the methods ``_plot_traj`` and ``_pretty``: 
    """

    def __init__(
        self, mass, thrust, isp,
        mu, freemass, freetime, alpha, bound,
        atol, rtol
    ):

        # spacecraft
        self.sc = pk.sims_flanagan.spacecraft(mass, thrust, isp)

        # indirect leg
        self.leg = pk.pontryagin.leg(
            sc=self.sc, mu=mu, freemass=freemass, freetime=freetime, alpha=alpha, bound=bound
        )

        # integration parametres
        if all([(isinstance(par, float) or isinstance(par, int)) for par in [atol, rtol]]):
            self.atol = float(atol)
            self.rtol = float(rtol)
        else:
            raise TypeError(
                "Both atol and rtol must be an instance of either float or int.")


    def get_nobj(self):
        return 1

    def get_nec(self):
        return self.leg.nec

    def plot_traj(self, z, mark="k.-", atol=1e-12, rtol=1e-12, units=pk.AU, axes = None):
        """This function plots the 3 dimensional spacecraft trajectory, given a solution chromosome.

        Args:
            - z (``list``, ``tuple``, ``numpy.ndarray``): Decision chromosome, e.g. (``pygmo.population.champion_x``).
            - mark (``string``): matplotlib marker.
            - atol (``float``, ``int``): absolute integration tolerance.
            - rtol (``float``, ``int``): relative integration tolerance.
            - units (``float``, ``int``): units by which to scale the trajectory dimensions.

        """

        # set problem
        self.fitness(z)

        # figure
        if axes is None:
            fig = plt.figure()
            axes = fig.gca(projection='3d')
        elif not isinstance(axes, Axes3D):
            raise TypeError(
                "Axis must be instance of matplotlib.axes._subplots.Axes3DSubplot.")

        # Sun
        axes.scatter([0], [0], [0], color='y')

        # leg
        self.leg.plot_traj(axes, mark, atol, rtol, units)

        # problem specifics
        self._plot_traj(z, axes, units)

        return axes

    def plot_control(self, z, mark="k.-", atol=1e-12, rtol=1e-12, axes = None):
        """Plots the control profile of the trajectory, as a function of time.

        Args:
            - z (``list``, ``tuple``, ``numpy.ndarray``): Decision chromosome, e.g. (``pygmo.population.champion_x``).
            - mark (``string``): matplotlib marker.
            - atol (``float``, ``int``): absolute integration tolerance.
            - rtol (``float``, ``int``): relative integration tolerance.

        """

        # set problem
        self.fitness(z)

        # create figure
        if axes is None:
            fig = plt.figure()
            axes = fig.gca()

        # leg
        self.leg.plot('tof', 'u', mark=mark, atol=atol, rtol=rtol, xlabel="Time [mjd2000]", ylabel="Throttle [ND]", axes = axes)

        return axes

    def get_traj(self, z):
        """Retrieves the trajectory information.
        ::

            traj = [[t0, x0, y0, z0, vx0, vy0, vz0, m0, u0, ux0, uy0, uz0]
                    ...
                    [tf, xf, yf, zf, vxf, vyf, vzf, mf, uf, uxf, uyf, uzf]]

        Args:
            - z (``list``, ``tuple``, ``numpy.ndarray``): Decision chromosome, e.g. (``pygmo.population.champion_x``).
        """

        # set leg
        self.fitness(z)

        # get states [t, x, y, z, vx, vy, vz, m, lx, ly, lz, lvx, lvy, lvz, lm, umag, ux, uy, uz, H]
        x = self.leg.get_states()
        # we make sure the throttles have the correct magnitude (get_states returns a direction as defined by the primer)
        for t in x:
            t[-4] *= t[-5]
            t[-3] *= t[-5]
            t[-2] *= t[-5]
        return x

    def pretty(self, z):
        data = self.get_traj(z) 
        self._pretty(z)

        print("\nSpacecraft Initial Position (m)  : [{!r}, {!r}, {!r}]".format(data[0,1], data[0,2], data[0,3]))
        print("Spacecraft Initial Velocity (m/s): [{!r}, {!r}, {!r}]".format(data[0,4], data[0,5], data[0,6]))
        print("Spacecraft Initial Mass  (kg)    : {!r}".format(data[0,7]))

        print("Spacecraft Final Position (m)  : [{!r}, {!r}, {!r}]".format(data[-1,1], data[-1,2], data[-1,3]))
        print("Spacecraft Final Velocity (m/s): [{!r}, {!r}, {!r}]".format(data[-1,4], data[-1,5], data[-1,6]))
        print("Spacecraft Final Mass  (kg)    : {!r}".format(data[-1,7]))

class indirect_pt2pt(_indirect_base):
    """
    Represents an indirect trajectory optimisation problem between two Cartesian states with heliocentric dynamics.
    The class can be used as UDP in pagmo. It creates a constraint satisfaction problem (TPBVP) whose solution satisfies 
    the Maximum principle from Pontryagin

        The decision chromosome is
    ::

        z = [T, l0]
    """

    def __init__(self, 
        x0 = [-31870515844.499527, -148420915911.91995, -232032831.15150324, 31422.536803556501, -7233.4361630081712, -415.32767881137943, 1000],
        xf = [69865919029.435547, 217248258866.53787, 2834587855.9536147, -22145.563252920241, 9476.4925663980739, 742.7125434140745, 910.95094097436925],
        tof=[230, 280],
        thrust = 0.3,
        isp = 3000,
        mu = pk.MU_SUN,
        freetime=True, 
        alpha=0, 
        bound=True, 
        atol=1e-12, 
        rtol=1e-12):
        """
        Constructs an instance of the ``PyKEP.trajopt.indirect_pt2pt`` problem.

        Args:
            - x0 (``list``, ``tuple``, ``numpy.ndarray``): Departure state [m, m, m, m/s, m/s, m/s, kg].
            - xf (``list``, ``tuple``, ``numpy.ndarray``): Arrival state [m, m, m, m/s, m/s, m/s, kg].
            - tof (``list``): Transfer time bounds [days].
            - thrust (``float``, ``int``): Spacecraft maximum thrust [N].
            - isp (``float``, ``int``): Spacecraft specific impulse [s].
            - mu (``float``): Gravitational parametre of primary body [m^3/s^2].
            - freetime (``bool``): Activates final time transversality condition. Allows final time to vary.
            - alpha (``float``, ``int``): Homotopy parameter (0 -quadratic control, 1 - mass optimal)
            - bound (``bool``): Activates bounded control, in which the control throttle is bounded between 0 and 1, otherwise the control throttle is allowed to unbounded.
            - atol (``float``, ``int``): Absolute integration solution tolerance.
            - rtol (``float``, ``int``): Relative integration solution tolerance.
        """

        # Cartesian states
        if not all([(isinstance(x, list) or isinstance(x, tuple) or isinstance(x, np.ndarray)) for x in [x0, xf]]):
            raise TypeError("Both x0 and xf must be supplied as an instance of either list, tuple, or numpy.ndarray.")
        elif not all([len(x) == 7 for x in [x0, xf]]):
            raise TypeError("Both x0 and xf must be supplied with 7 dimensions.")
        else:
            self.x0 = pk.sims_flanagan.sc_state()
            self.x0.set(x0)
            self.xf = pk.sims_flanagan.sc_state()
            self.xf.set(xf)

        self.tof = tof

        # initialise base
        _indirect_base.__init__(
            self, x0[-1], thrust, isp, mu, True, freetime, alpha, bound,
            atol, rtol
        )

    def fitness(self, z):

        # times
        t0 = pk.epoch(0)
        tf = pk.epoch(z[0])

        # costates
        l0 = np.asarray(z[1:])

        # set leg
        self.leg.set(t0, self.x0, l0, tf, self.xf)

        # equality constraints
        ceq = self.leg.mismatch_constraints(atol=self.atol, rtol=self.rtol)

        return np.hstack(([1, ceq]))

    def get_bounds(self):
        lb = [self.tof[0]] + [-100] * 7
        ub = [self.tof[1]] + [100] * 7
        return (lb, ub)

    def _plot_traj(self, z, axes, units):

        # states
        x0 = self.leg.x0
        xf = self.leg.xf

        # times
        t0 = pk.epoch(self.leg.t0)
        tf = pk.epoch(self.leg.tf)

        # Computes the osculating Keplerian elements at start and arrival
        elem0 = list(pk.ic2par(x0[0:3], x0[3:6], self.leg.mu))
        elemf = list(pk.ic2par(xf[0:3], xf[3:6], self.leg.mu))

        # Converts the eccentric anomaly into eccentric anomaly
        elem0[5]  = elem0[5] - elem0[1] * np.sin(elem0[5])
        elemf[5]  = elemf[5] - elemf[1] * np.sin(elemf[5])

        # Creates two virtual keplerian planets with the said elements
        kep0 = pk.planet.keplerian(t0, elem0)
        kepf = pk.planet.keplerian(tf, elemf)

        # Plots the departure and arrival osculating orbits
        pk.orbit_plots.plot_planet(kep0, t0, units=units, color=(0.8, 0.8, 0.8), ax=axes)
        pk.orbit_plots.plot_planet(kepf, tf, units=units, color=(0.8, 0.8, 0.8), ax=axes)

    def _pretty(self, z):
        print("\nPoint to point transfer: ")
        print("\nFrom: " + str(self.x0))
        print("To: " + str(self.xf))
        print("Time of flight (days): {!r} ".format(z[0]))

class indirect_pl2pl(_indirect_base):
    """Represents an indirect trajectory optimisation problem between two planets.

    Decision chromosome is
    ::

        z = [t0, T, l0]

    """

    def __init__(self, p0, pf, mass, thrust, isp, atol, rtol, t0, tof, freetime=True, alpha=1, bound=True, mu=pk.MU_SUN):
        """
        Initialises ``PyKEP.trajopt.indirect_pl2pl`` problem.

        Args:
            - p0 (``str``): Departure planet name.
            - pf (``str``): Arrival planet name.
            - mass (``float``, ``int``): Spacecraft wet mass [kg].
            - thrust (``float``, ``int``): Spacecraft maximum thrust [N].
            - isp (``float``, ``int``): Spacecraft specific impulse [s].
            - atol (``float``, ``int``): Absolute integration solution tolerance.
            - rtol (``float``, ``int``): Relative integration solution tolerance.
            - t0 (``list``): Launch epoch bounds [MJD2000].
            - tof (``list``): Transfer time bounds [days].
            - freetime (``bool``): Activates final time transversality condition. Allows final time to vary.
            - alpha (``float``, ``int``): Homotopy parametre, governing the degree to which the theoretical control law is intended to reduce propellant expenditure or energy.
            - bound (``bool``): Activates bounded control, in which the control throttle is bounded between 0 and 1, otherwise the control throttle is allowed to unbounded.
            - mu (``float``): Gravitational parametre of primary body [m^3/s^2].
        """

        # initialise base
        _indirect_base.__init__(
            self, mass, thrust, isp, mu, True, freetime, alpha, bound,
            atol, rtol
        )

        # planets
        if all([isinstance(pl, str) for pl in [p0, pf]]):
            self.p0 = pk.planet.jpl_lp(p0)
            self.pf = pk.planet.jpl_lp(pf)
        else:
            raise TypeError("Planet names must be supplied as str.")

        self.t0 = t0
        self.tof = tof

    def fitness(self, z):

        # times
        t0 = pk.epoch(z[0])
        tf = pk.epoch(z[0] + z[1])

        # initial costates
        l0 = np.asarray(z[2:])

        # Cartesian states
        r0, v0 = self.p0.eph(t0)
        rf, vf = self.pf.eph(tf)

        # states
        x0 = pk.sims_flanagan.sc_state(r0, v0, self.sc.mass)
        xf = pk.sims_flanagan.sc_state(rf, vf, self.sc.mass / 10)

        # set leg
        self.leg.set(t0, x0, l0, tf, xf)

        # propagate leg
        ceq = self.leg.mismatch_constraints(atol=self.atol, rtol=self.rtol)

        # final mass
        mf = self.leg.trajectory[-1, 6]

        return np.hstack(([1, ceq]))

    def get_bounds(self):
        lb = [self.t0[0], self.tof[0]] + [-1e2] * 7
        ub = [self.t0[1], self.tof[1]] + [1e2] * 7
        return (lb, ub)

    def _plot_traj(self, z, axes, units):
        """Plots spacecraft trajectory.

        Args:
            - z (``tuple``, ``list``, ``numpy.ndarray``): Decision chromosome.
            - atol (``float``, ``int``): Absolute integration solution tolerance.
            - rtol (``float``, ``int``): Relative integration solution tolerance.
            - units (``float``, ``int``): Length unit by which to normalise data.

        Examples:
            >>> prob.extract(PyKEP.trajopt.indirect_pl2pl).plot_traj(pop.champion_x)
        """

        # departure and arrival times
        t0 = pk.epoch(z[0])
        tf = pk.epoch(z[0] + z[1])

        # planets
        pk.orbit_plots.plot_planet(
            self.p0, t0=t0, units=units, ax=axes, color=(0.8, 0.8, 0.8))
        pk.orbit_plots.plot_planet(
            self.pf, t0=tf, units=units, ax=axes, color=(0.8, 0.8, 0.8))

class indirect_or2or(_indirect_base):
    """Represents an indirect trajectory optimisation problem between two orbits.

    Decision chromosome is
    ::

        z = [T, M0, Mf, l0]

    """

    def __init__(self, elem0, elemf, mass, thrust, isp, atol, rtol, tof, freetime=True, alpha=1, bound=True, mu=pk.MU_SUN):
        """Initialises ``PyKEP.trajopt.indirect_or2or`` problem.

        Args:
            - elem0 (``list``, ``tuple``, ``numpy.ndarray``): Departure Keplerian elements (mutable eccentric anomaly).
            - elemf (``list``, ``tuple``, ``numpy.ndarray``): Arrival Keplerian elements (mutable eccentric anomaly).
            - mass (``float``, ``int``): Spacecraft wet mass [kg].
            - thrust (``float``, ``int``): Spacecraft maximum thrust [N].
            - isp (``float``, ``int``): Spacecraft specific impulse [s].
            - atol (``float``, ``int``): Absolute integration solution tolerance.
            - rtol (``float``, ``int``): Relative integration solution tolerance.
            - tof (``list``): Transfer time bounds [days].
            - freetime (``bool``): Activates final time transversality condition. Allows final time to vary.
            - alpha (``float``, ``int``): Homotopy parametre, governing the degree to which the theoretical control law is intended to reduce propellant expenditure or energy.
            - bound (``bool``): Activates bounded control, in which the control throttle is bounded between 0 and 1, otherwise the control throttle is allowed to unbounded.
            - mu (``float``): Gravitational parametre of primary body [m^3/s^2].

        """

        # initialise base
        _indirect_base.__init__(
            self, mass, thrust, isp, mu, True, freetime, alpha, bound,
            atol, rtol
        )

        # Keplerian elements
        self.elem0 = np.asarray(elem0)
        self.elemf = np.asarray(elemf)

        # Time of flight bounds
        self.tof = tof

    def fitness(self, z):

        # departure and arrival times
        t0 = pk.epoch(0)
        tf = pk.epoch(z[0])

        # departure and arrival eccentric anomolies
        M0 = z[1]
        Mf = z[2]

        # departure costates
        l0 = np.asarray(z[3:])

        # set Keplerian elements
        elem0 = np.hstack([self.elem0[:5], [M0]])
        elemf = np.hstack([self.elemf[:5], [Mf]])

        # compute Cartesian states
        r0, v0 = pk.par2ic(elem0, self.leg.mu)
        rf, vf = pk.par2ic(elemf, self.leg.mu)

        # departure and arrival states (xf[6] is unused)
        x0 = pk.sims_flanagan.sc_state(r0, v0, self.sc.mass)
        xf = pk.sims_flanagan.sc_state(rf, vf, self.sc.mass / 10)

        # set leg
        self.leg.set(t0, x0, l0, tf, xf)

        # equality constraints
        ceq = self.leg.mismatch_constraints(atol=self.atol, rtol=self.rtol)

        # final mass
        obj = self.leg.trajectory[-1, -1]

        # Transversality conditions
        # At start
        lambdas0 = np.array(self.leg.trajectory[0, 7:13])
        r0norm = np.sqrt(r0[0]*r0[0]+r0[1]*r0[1]+r0[2]*r0[2])
        tmp = - pk.MU_SUN / r0norm**3
        tangent = np.array([v0[0],v0[1],v0[2], tmp * r0[0], tmp * r0[1], tmp * r0[2]])
        tangent_norm = np.linalg.norm(tangent)
        tangent = tangent / tangent_norm
        T0 = np.dot(lambdas0,tangent)

        # At end
        lambdasf = np.array(self.leg.trajectory[-1, 7:13])
        rfnorm = np.sqrt(rf[0]*rf[0]+rf[1]*rf[1]+rf[2]*rf[2])
        tmp = - pk.MU_SUN / rfnorm**3
        tangent = np.array([vf[0],vf[1],vf[2], tmp * rf[0], tmp * rf[1], tmp * rf[2]])
        tangent_norm = np.linalg.norm(tangent)
        tangent = tangent / tangent_norm
        Tf = np.dot(lambdasf,tangent)

        return np.hstack(([1], ceq, [T0,Tf]))

    def get_nec(self):
        return self.leg.nec + 2

    def get_bounds(self):
        lb = [self.tof[0], -4*np.pi, -4*np.pi] + [-1e2] * 7
        ub = [self.tof[1], 4*np.pi, 4*np.pi] + [1e2] * 7
        return (lb, ub)

    def _plot_traj(self, z, axes, units):
        """Plots spacecraft trajectory.

        Args:
            - z (``tuple``, ``list``, ``numpy.ndarray``): Decision chromosome.
            - atol (``float``, ``int``): Absolute integration solution tolerance.
            - rtol (``float``, ``int``): Relative integration solution tolerance.
            - units (``float``, ``int``): Length unit by which to normalise data.

        Examples:
            >>> prob.extract(PyKEP.trajopt.indirect_or2or).plot_traj(pop.champion_x)
        """

        # times
        t0 = pk.epoch(0)
        tf = pk.epoch(z[0])

        # Mean Anomalies
        M0 = z[1] - self.elem0[1] * np.sin(z[1])
        Mf = z[2] - self.elemf[1] * np.sin(z[2])

        elem0 = np.hstack([self.elem0[:5], [M0]])
        elemf = np.hstack([self.elemf[:5], [Mf]])

        # Keplerian points 
        kep0 = pk.planet.keplerian(t0, elem0)
        kepf = pk.planet.keplerian(tf, elemf)

        # planets
        pk.orbit_plots.plot_planet(
            kep0, t0=t0, units=units, ax=axes, color=(0.8, 0.8, 0.8))
        pk.orbit_plots.plot_planet(
            kepf, t0=tf, units=units, ax=axes, color=(0.8, 0.8, 0.8))

class indirect_pt2or(_indirect_base):
    """Represents an indirect trajectory optimisation problem between a Cartesian state and an orbit.

    Decision chromosome is
    ::

        z = [T, Mf, l0]

    """

    def __init__(self, x0, elemf, mass, thrust, isp, atol, rtol, tof, freetime=True, alpha=1, bound=True, mu=pk.MU_SUN):
        """Initialises ``PyKEP.trajopt.indirect_pt2or`` problem.

        Args:
            - x0 (``list``, ``tuple``, ``numpy.ndarray``): Departure state [m, m, m, m/s, m/s, m/s, kg].
            - elemf (``list``, ``tuple``, ``numpy.ndarray``): Arrival Keplerian elements (mutable eccentric anomaly).
            - mass (``float``, ``int``): Spacecraft wet mass [kg].
            - thrust (``float``, ``int``): Spacecraft maximum thrust [N].
            - isp (``float``, ``int``): Spacecraft specific impulse [s].
            - atol (``float``, ``int``): Absolute integration solution tolerance.
            - rtol (``float``, ``int``): Relative integration solution tolerance.
            - tof (``list``): Transfer time bounds [days].
            - freetime (``bool``): Activates final time transversality condition. Allows final time to vary.
            - alpha (``float``, ``int``): Homotopy parametre, governing the degree to which the theoretical control law is intended to reduce propellant expenditure or energy.
            - bound (``bool``): Activates bounded control, in which the control throttle is bounded between 0 and 1, otherwise the control throttle is allowed to unbounded.
            - mu (``float``): Gravitational parametre of primary body [m^3/s^2].

        """

        # initialise base
        _indirect_base.__init__(
            self, mass, thrust, isp, mu, True, freetime, alpha, bound,
            atol, rtol
        )


        # departure state and arrival Keplerian elements
        self.x0 = np.asarray(x0, np.float64)
        self.elemf = np.asarray(elemf, np.float64)
        self.tof = tof

    def fitness(self, z):

        # times
        t0 = pk.epoch(0)
        tf = pk.epoch(z[0])

        # final eccentric anomaly
        Mf = z[1]

        # intial costates
        l0 = np.asarray(z[2:])

        # set arrival Keplerian elements
        self.elemf[5] = Mf

        # departure state
        x0 = pk.sims_flanagan.sc_state(self.x0[0:3], self.x0[3:6], self.x0[6])

        # compute Cartesian arrival state
        rf, vf = pk.par2ic(self.elemf, self.leg.mu)
        xf = pk.sims_flanagan.sc_state(rf, vf, self.sc.mass / 10)

        # set leg
        self.leg.set(t0, x0, l0, tf, xf)

        # equality constraints
        ceq = self.leg.mismatch_constraints(atol=self.atol, rtol=self.rtol)

        # final mass
        # mf = self.leg.trajectory[-1, 6]

        # Transversailty condition at the end
        lambdasf = np.array(self.leg.trajectory[-1, 7:13])
        rfnorm = np.sqrt(rf[0]*rf[0]+rf[1]*rf[1]+rf[2]*rf[2])
        tmp = - pk.MU_SUN / rfnorm**3
        tangent = np.array([vf[0],vf[1],vf[2], tmp * rf[0], tmp * rf[1], tmp * rf[2]])
        tangent_norm = np.linalg.norm(tangent)
        tangent = tangent / tangent_norm
        Tf = np.dot(lambdasf,tangent)

        return np.hstack(([1], ceq, [Tf]))

    def get_nec(self):
        return self.leg.nec + 1

    def get_bounds(self):
        lb = [self.tof[0], -4*np.pi] + [-1e2] * 7
        ub = [self.tof[1], 4*np.pi] + [1e2] * 7
        return (lb, ub)

    def _plot_traj(self, z, axes, units=pk.AU):
        """Plots spacecraft trajectory.

        Args:
            - z (``tuple``, ``list``, ``numpy.ndarray``): Decision chromosome.
            - atol (``float``, ``int``): Absolute integration solution tolerance.
            - rtol (``float``, ``int``): Relative integration solution tolerance.
            - units (``float``, ``int``): Length unit by which to normalise data.

        Examples:
            >>> prob.extract(PyKEP.trajopt.indirect_pt2or).plot_traj(pop.champion_x)
        """

        # times
        t0 = pk.epoch(0)
        tf = pk.epoch(z[1])

        # Keplerian elements of the osculating orbit at start
        elem0 = pk.ic2par(self.x0[0:3], self.x0[3:6], self.leg.mu)
        # Eccentric to Mean Anomaly
        elemf[5]  = elemf[5] - elemf[1] * np.sin(elemf[5])

        # Mean Anomaly at the target orbit
        Mf = z[1] - self.elemf[1] * np.sin(z[1])

        elemf = np.hstack([self.elemf[:5], [Mf]])

        # Keplerian elements
        kep0 = pk.planet.keplerian(t0, elem0)
        kepf = pk.planet.keplerian(tf, self.elemf)

        # plot departure and arrival
        pk.orbit_plots.plot_planet(kep0, t0, units=units, color=(0.8, 0.8, 0.8), ax=axes)
        pk.orbit_plots.plot_planet(kepf, tf, units=units, color=(0.8, 0.8, 0.8), ax=axes)
