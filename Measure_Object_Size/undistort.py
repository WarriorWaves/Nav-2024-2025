import cv2
import numpy as np

print("imported cv2")
points = []


def click_event(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(img, (x, y), 1, (0, 0, 255), -1)
        cv2.imshow("image", img)

        if len(points) == 4:
            pts1 = np.float32(points)
            dx = points[0][0]
            dy = points[0][1]

            width = max(
                np.linalg.norm(pts1[0] - pts1[1]), np.linalg.norm(pts1[2] - pts1[3])
            )
            height = max(
                np.linalg.norm(pts1[0] - pts1[3]), np.linalg.norm(pts1[1] - pts1[2])
            )
            pts2 = np.float32(
                [
                    [0 + dx, 0 + dy],
                    [width + dx, 0 + dy],
                    [width + dx, height + dy],
                    [0 + dx, height + dy],
                ]
            )

            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            h, w = img.shape[:2]
            result = cv2.warpPerspective(img, matrix, (w, h))
            canvas_height = int(max(h, height) * 1.5)
            canvas_width = int(max(w, width) * 1.5)
            canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
            y_offset = (canvas_height - h) // 2
            x_offset = (canvas_width - w) // 2
            canvas[y_offset : y_offset + h, x_offset : x_offset + w] = result
            cv2.imshow("corrected image", result)
            cv2.imwrite("./image.png", result)


img = cv2.imread(
    "/Users/aayanmaheshwari/Desktop/MATE/rang23-24/viewcam/2024-06-11 17:42:03.jpg"
)
cv2.imshow("image", img)
cv2.setMouseCallback("image", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()