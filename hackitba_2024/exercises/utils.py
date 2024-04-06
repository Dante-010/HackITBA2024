from math import floor
from .models import *
import random

# Create your views here.
def percent_calc(act, total):
  return min(100, floor(act / total * 100))

def update_progress(username, achiv_name):
  user = User.objects.get(pk = username)
  achiv = Achievement.objects.get(pk = achiv_name)
  user_achiv = UserAchievement.objects.filter(user_id = username, achievement_id = achiv_name).first()
  
  if (user_achiv.is_completed()):
    return
  
  if (achiv.get_type() == STREAK):
    act = user.get_streak()
  elif (achiv.get_type() == ACHIV_AMOUNT):
    act = UserAchievement.objects.filter(user_id = username).count()
  elif (achiv.get_type() == EXER_AMOUNT):
    act = UserExercise.objects.filter(user_id = username).count()
  elif (achiv.get_type() == EXER_DIFF):
    act = Exercise.objects.filter(userexercise__username=username,
                                  userexercise__difficulty=achiv.get_difficulty()).count()
  elif (achiv.get_type() == EXER_TYPE):
    act = Exercise.objects.filter(userexercise__username=username,
                                  userexercise__type=achiv.get_type()).count()
  elif (achiv.get_type() == EXER_DIFF_TYPE):
    act = Exercise.objects.filter(userexercise__username=username,
                                  userexercise__difficulty=achiv.get_difficulty(),
                                  userexercise__type=achiv.get_type()).count()
  
  user_achiv.set_progress(percent_calc(act + 1, achiv.get_limit()))
  user_achiv.save()
  if (user_achiv.is_completed()):
    update_progress(user, ACHIV_AMOUNT)

STREAK_ACHIEVEMENTS_DAYS = (5, 10, 25, 50, 100, 365)

def increase_streak(username):
  user = User.objects.get(pk = username)
  user.set_streak(user.set_streak() + 1)
  user.save()
  for s in STREAK_ACHIEVEMENTS_DAYS:
    update_progress(username, f"STREAK_{s}")

# Function to be executed every day
def remove_streak(username):
  user = User.objects.get(pk=username)
  user.set_streak(0)
  user.save()
  for s in STREAK_ACHIEVEMENTS_DAYS:
    update_progress(username, f"STREAK_{s}")

def change_day():
  for user in User.object.all():
    if user.get_entered_today() == False:
      remove_streak(user)
    else:
      user.set_entered_today(False)
      user.save()


def create_achievement(achiv_description, achiv_limit, achiv_type, achiv_exer_difficulty="", achiv_exer_type=""):
  if (achiv_type not in VALID_ACHIEVEMENTS): # ERROR
    return print("Invalid achievement type.")
  achiv_name = f"{achiv_type}_{achiv_limit}"
  Achievement.objects.create(
    name = achiv_name,
    description = achiv_description,
    limit = achiv_limit,
    type = achiv_type,
    exer_difficulty = achiv_exer_difficulty,
    exer_type = achiv_exer_type
  )

def modify_achievement(achiv_name, new_achiv_description, new_achiv_limit, new_achiv_type):
  if (new_achiv_type not in VALID_ACHIEVEMENTS): # ERROR
    return print("Invalid achievement type.")
  new_achiv_name = f"{new_achiv_type}_{new_achiv_limit}"
  achiv = Achievement.objects.get(pk = achiv_name)
  achiv.set_name(new_achiv_name)
  achiv.set_description(new_achiv_description)
  achiv.set_limit(new_achiv_limit)
  achiv.set_type(new_achiv_type)
  achiv.save()

def delete_achievement(achiv_name):
  achiv = Achievement.objects.get(pk = achiv_name)
  achiv.delete()

def create_exercise(exer_title, exer_description, exer_difficulty, exer_type, exer_image):
  if (exer_difficulty not in VALID_DIFFICULTIES):
    return print("Invalid exercise difficulty.")
  if (exer_type not in VALID_EXERCISES):
    return print("Invalid exercise type.")
  cant = Exercise.objects.filter(difficulty = exer_difficulty, type = exer_type).count()
  exer_name = f"{exer_type}_{exer_difficulty}_{cant+1}"
  Exercise.objects.create(
    name = exer_name,
    title = exer_title,
    description = exer_description,
    difficulty = exer_difficulty,
    type = exer_type,
    image = exer_image
  )

def delete_exercise(exer_name):
  exercise = Exercise.objects.get(pk = exer_name)
  exercise.delete()

def read_and_parse(filename, word_amount):
  try:
    with open(f'../texto/{filename}.txt', 'r') as file:
      text_content = file.read().upper().split('\n')
  except FileNotFoundError:
    return []
  filtered = random.sample(text_content, k = word_amount)
  parsed = list(map(lambda pair: tuple(pair.split(',')), filtered))
  corrected = list(map(lambda p: (
    {
      'text': p[0],
      'correct': True
    },
    {
      'text': p[1],
      'correct': False
    }
  ), parsed))
  reordered = list(map(lambda p: random.sample(p, k=len(p)), corrected))
  return reordered
