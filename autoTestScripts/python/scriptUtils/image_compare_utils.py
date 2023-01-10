import cv2
import numpy as np
# from skimage.measure import compare_ssim as ssim
# from skimage.measure import compare_mse as mse_ski
from skimage.metrics import peak_signal_noise_ratio as compare_psnr
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as compare_mse
import matplotlib.pyplot as plt
from autoTestScripts.python.scriptUtils import constant

def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageB.shape[1])
    return err


def compare_image_ndarray(refer_image_path: str, image_test_ndarray: np.ndarray):
    result = {}
    refer_image = cv2.imread(refer_image_path, cv2.IMREAD_GRAYSCALE)
    # 与compress_rate有关, 为 0.4 时，1280,720乘以0.4
    refer_image = cv2.resize(refer_image, (512, 288))
    # m1 = mse(refer_image, image_test)
    # 均方误差
    # MSE因为是均方差，值越小代表越相同，0 代表完全相同。
    mse = compare_mse(refer_image, image_test_ndarray)
    result['mse'] = mse
    # 结构相似性 SSIM的值范围[-1, 1]，1代表完全相同。
    s = ssim(refer_image, image_test_ndarray)
    result['ssim'] = s
    # 峰值信噪比
    pnsr = compare_psnr(refer_image, image_test_ndarray)
    result['pnsr'] = pnsr
    print("MSE With Ski: %.2f, SSIM: %.2f pnsr: %.2f" % (mse, s, pnsr))
    return result


def compare_image(refer_image, image_test, title):
    # m1 = mse(refer_image, image_test)
    # 均方误差
    # MSE因为是均方差，值越小代表越相同，0 代表完全相同。
    mse = compare_mse(refer_image, image_test)
    # 结构相似性 SSIM的值范围[-1, 1]，1代表完全相同。
    s = ssim(refer_image, image_test)
    # 峰值信噪比
    pnsr = compare_psnr(refer_image, image_test)

    fig = plt.figure(title)
    plt.suptitle("MSE With Ski: %.2f, SSIM: %.2f pnsr: %.2f" % (mse, s, pnsr))

    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(refer_image, cmap=plt.cm.gray)
    plt.axis("off")

    ax = fig.add_subplot(1, 2, 2)
    plt.imshow(image_test, cmap=plt.cm.gray)
    plt.axis("off")

    plt.show()


if __name__ == "__main__":
    template_image_path = "D:\Python\coocaaautotest\\autoTestScripts\python\stagesepx_with_keras\picture_for_train\TestLocalMediaBootTime\splash.png"
    image_path = 'D:\Python\coocaaautotest\\autoTestScripts\python\stagesepx_with_keras\picture\\forecast\TestLocalMediaBootTime\cr_0.2_th_0.97_os_2_block_6\\forecast_stable_TestLocalMediaBootTime_2022-12-26-19-05-59\\2\TestLocalMediaBootTime_2022-12-26-19-05-59_149_2.466666666666667.png'

    template_image = cv2.imread(template_image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # print(origine.shape, changed.shape)
    # orin_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
    # changed_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    orin_gray = template_image
    changed_gray = image
    # compare_image(orin_gray, orin_gray, "Original vs. Original")
    # compare_image(changed_gray, changed_gray, "Changed vs. Changed")
    compare_image(orin_gray, changed_gray, "Original vs. Changed")
    # image = cv2.imread('test.jpg')
    # cv2.imwrite('image01-0.jpg', image[:, :400])
    # cv2.imwrite('image01-1.jpg', image[:, 400::])
