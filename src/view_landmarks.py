import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2

class LandmarkVisualizerApp(QMainWindow):
    def __init__(self, animation_data, video_path):
        super().__init__()
        self.animation_data = animation_data
        self.video_path = video_path
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Landmark Visualizer')
        self.setGeometry(100, 100, 1200, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Create horizontal layout for video frame and 3D plot
        h_layout = QHBoxLayout()

        # Video frame
        self.video_label = QLabel()
        h_layout.addWidget(self.video_label)

        # 3D plot
        self.figure = Figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111, projection='3d')
        h_layout.addWidget(self.canvas)

        layout.addLayout(h_layout)

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.animation_data["keyframes"]) - 1)
        self.slider.valueChanged.connect(self.update_frame)
        layout.addWidget(self.slider)

        self.update_frame(0)

    def update_frame(self, frame_index):
        num_animation_frames = len(self.animation_data["keyframes"])
        # Update video frame
        cap = cv2.VideoCapture(self.video_path)
        total_num_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_frame_index = int(frame_index * total_num_video_frames / num_animation_frames)
        cap.set(cv2.CAP_PROP_POS_FRAMES, video_frame_index)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))

        # Update 3D plot
        self.ax.clear()
        self.plot_landmarks(self.animation_data["keyframes"][frame_index]["landmarks"])
        self.canvas.draw()

    def plot_landmarks(self, landmarks):
        if 'pose' in landmarks:
            pose_data = landmarks['pose']
            for part, coords in pose_data.items():
                self.ax.scatter(*coords, c='r', marker='o')
                self.add_text_label(coords, part)

            # Draw body connections
            connections = [
                ('head', 'left_shoulder'),
                ('head', 'right_shoulder'),
                ('left_shoulder', 'right_shoulder'),
                ('left_shoulder', 'left_elbow'),
                ('right_shoulder', 'right_elbow'),
                ('left_elbow', 'left_wrist'),
                ('right_elbow', 'right_wrist'),
                ('left_shoulder', 'left_hip'),
                ('right_shoulder', 'right_hip'),
                ('left_hip', 'right_hip'),
            ]

            for start, end in connections:
                if start in pose_data and end in pose_data:
                    self.ax.plot(*zip(pose_data[start], pose_data[end]), c='cyan')

        # Set axis limits
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)

        # Set labels
        self.ax.set_xlabel('X (Left/Right)')
        self.ax.set_ylabel('Y (Front/Back)')
        self.ax.set_zlabel('Z (Top/Bottom)')

        # Add coordinate system arrows
        arrow_length = 0.2
        self.ax.quiver(0, 0, 0, arrow_length, 0, 0, color='r', arrow_length_ratio=0.1)
        self.ax.quiver(0, 0, 0, 0, arrow_length, 0, color='g', arrow_length_ratio=0.1)
        self.ax.quiver(0, 0, 0, 0, 0, arrow_length, color='b', arrow_length_ratio=0.1)

        # Add text labels for axes
        self.ax.text(arrow_length, 0, 0, "X", color='r')
        self.ax.text(0, arrow_length, 0, "Y", color='g')
        self.ax.text(0, 0, arrow_length, "Z", color='b')

        self.ax.set_title('3D Landmarks (Blender Coordinate System)')

    def add_text_label(self, point, label):
        self.ax.text(*point, label, fontsize=8, ha='right', va='bottom')


if __name__ == "__main__":
    video_path = 'videos/maybe_1.mp4'
    animation_data_path = 'animation_data.json'
    with open(animation_data_path, 'r') as f:
        animation_data = json.load(f)
    app = QApplication([])
    ex = LandmarkVisualizerApp(animation_data, video_path)
    ex.show()
    app.exec_()