from .actions import ReviewsLoader
from .scene import ReviewsScene


scene = ReviewsScene
actions = [ReviewsLoader]
tasks_endpoints = ['tasks/get_available/products?stage=3']
