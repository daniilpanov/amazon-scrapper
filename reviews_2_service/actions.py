import requests
from PyQt5.QtCore import QObject, pyqtSlot, QJsonValue


class ReviewsLoader(QObject):
    def __init__(self, scene):
        super(ReviewsLoader, self).__init__()
        self.scene = scene

    @pyqtSlot(QJsonValue)
    def loadPage(self, reviews_from_page: QJsonValue):
        if reviews_from_page.isArray():
            reviews_from_page = reviews_from_page.toArray()
        elif reviews_from_page.isObject():
            reviews_from_page = [reviews_from_page.toObject()]
        requests.post('http://localhost:8832/products/set_result/reviews', json=reviews_from_page)

    @pyqtSlot(int, int)
    def fail(self, index, page):
        self.scene.index = index
        self.scene.page_number = page
        next(self.scene)
