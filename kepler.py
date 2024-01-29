import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import matplotlib.patches as mpatches
from pathlib import Path
import ffmpeg

ECCENTRICITY = 0.7
SEMIMAJOR = 1.

time = np.linspace(0, 1, num=1000)
mean_anomaly = np.linspace(0, 2*np.pi, num=1000)

# colors picked from https://davidmathlogic.com/colorblind
MA_COLOR = '#648FFF'
EA_COLOR = '#DC267F'
TA_COLOR = '#FFB000'

ARC_RADIUS = 0.12

def color_arc(center, initial_angle, final_angle, color, arc_radius=ARC_RADIUS):
    angle_span = np.linspace(initial_angle, final_angle, num=100)
    x0, y0 = center
    x = np.append([x0], x0 + arc_radius * np.cos(angle_span))
    y = np.append([y0], y0 + arc_radius * np.sin(angle_span))
    plt.fill(x, y, color=color)

def eccentric_anomaly_from_mean(mean_anomaly, eccentricity):
    func = lambda E : E - eccentricity*np.sin(E) - mean_anomaly
    return fsolve(func, x0=mean_anomaly)

# ṡolve for eccentric anomaly by using Kepler's Equation
eccentric_anomaly = eccentric_anomaly_from_mean(mean_anomaly, ECCENTRICITY)

# formula from https://ui.adsabs.harvard.edu/abs/1973CeMec...7..388B/abstract
# avoids numerical issues
beta = ECCENTRICITY / (1+np.sqrt(1 - ECCENTRICITY**2))
true_anomaly = eccentric_anomaly + 2 * np.arctan2(beta * np.sin(eccentric_anomaly), 1 - beta * np.cos(eccentric_anomaly))

semiminor = SEMIMAJOR * np.sqrt(1 - ECCENTRICITY**2)
focal_distance = SEMIMAJOR * ECCENTRICITY

def plot_anomalies_graph():
    plt.plot(time, true_anomaly, label='True anomaly', c=TA_COLOR)
    plt.plot(time, eccentric_anomaly, label='Eccentric anomaly', c=EA_COLOR)
    plt.plot(time, mean_anomaly, label='Mean anomaly',  c=MA_COLOR)

    plt.xticks([0, 0.25, 0.5, 0.75, 1], ['0', '0.25', '0.5', '0.75', '1'])
    plt.yticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi], ['0', 'π/2', 'π', '3π/2', '2π'])
    plt.xlabel('Time since perihelion [$t / T$]')
    plt.ylabel('Anomaly')
    plt.grid('on')
    plt.legend()

    plt.gca().set_aspect(1 / (2 * np.pi))
    plt.tight_layout()
    plt.savefig('anomalies.png', dpi=300)
    plt.close()

r1 = SEMIMAJOR * (1 - ECCENTRICITY**2) / (1 + ECCENTRICITY * np.cos(true_anomaly))
x1 = (r1 * np.cos(true_anomaly)) + focal_distance
y1 = (r1 * np.sin(true_anomaly))

x2 = SEMIMAJOR * np.cos(eccentric_anomaly)
y2 = SEMIMAJOR * np.sin(eccentric_anomaly)

def plot_angles_index(index, frames_folder):

    plt.plot(x1, y1, c='black', lw=2)
    plt.plot(x2, y2, c='black', lw=1)
    plt.gca().set_aspect(1)

    plt.plot([0, x2[index]], [0, y2[index]], c=EA_COLOR)
    plt.plot([0, focal_distance], [0, 0], c=EA_COLOR)
    color_arc((0, 0), 0, eccentric_anomaly[index], color=EA_COLOR)

    plt.plot([focal_distance, x1[index]], [0, y1[index]], c=TA_COLOR)
    plt.plot([focal_distance, SEMIMAJOR], [0, 0], c=TA_COLOR)
    color_arc((focal_distance, 0), 0, true_anomaly[index], color=TA_COLOR)

    color_arc((1.4*SEMIMAJOR, 0.), 0, mean_anomaly[index], color=MA_COLOR, arc_radius=2*ARC_RADIUS)

    plt.xlim(-1.1*SEMIMAJOR, 1.7*SEMIMAJOR)
    plt.scatter(x1[index], y1[index], s=100, c='black', zorder=3)
    plt.scatter(focal_distance, 0, s=100, c='black', zorder=3)

    handles = []
    for color, label in zip(
        [EA_COLOR, TA_COLOR, MA_COLOR], 
        ['Eccentric anomaly', 'True anomaly', 'Mean anomaly']):
        handles.append(mpatches.Patch(color=color, label=label))
    plt.legend(handles=handles)
    plt.gca().axis('off')
    # plt.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

    plt.savefig(frames_folder / f'frame{index:04d}.png', dpi=300)
    plt.close()
    
def make_vid(
    frames_folder: Path,
    vid_name: str,
    framerate: int = 60,
    loop_amount: int = 1,
    ):
    
    (
        ffmpeg
        .input(
            str(frames_folder/'*.png'), 
            pattern_type='glob', 
            framerate=framerate, 
            s='1920x1440',
            **{'stream_loop': loop_amount-1})
        .output(vid_name)
        .overwrite_output()
        .run()
    )

    
if __name__ == '__main__':
    plot_anomalies_graph()
    
    this_folder = Path().resolve()
    frames_folder = this_folder / 'frames'
    
    if not frames_folder.exists():
        frames_folder.mkdir()
    
    for index in range(1000):
        plot_angles_index(index, frames_folder)
    
    make_vid(frames_folder, str(this_folder / 'kepler.mp4'), loop_amount=3)