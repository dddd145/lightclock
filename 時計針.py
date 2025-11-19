import math
import pygame

# 定義
hari_length_m = 0.05
period_divider = 60
speed_of_light = 299792458

width, height = 800, 600
center_x, center_y = width // 4, height // 2
radius = 200
fps = 120

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 200, 0)
blue_default = (0, 0, 150)
light_magenta = (255, 0, 255)

panel_left = width // 2 + 10
panel_top = 20
panel_width = width // 2 - 20
panel_height = height - 40
scroll_speed = 20
panel_rect = pygame.Rect(panel_left, panel_top, panel_width, panel_height)

haris_data = []
extra_hari_count = 0
start_time = 0.0
scroll_y = 0

# 針計算関数
def calculate_hari_data(name, period_seconds, extra_count):
  angular_velocity = (2 * math.pi) / period_seconds
  tip_velocity_mps = hari_length_m * angular_velocity
  tip_velocity_kmh = tip_velocity_mps * 3.6
  light_speed_ratio = tip_velocity_mps / speed_of_light

  if tip_velocity_mps > speed_of_light:
    color = light_magenta
  else:
    color_val = max(50, 255 - extra_count * 40)
    color = (0, 0, color_val)

  return {
      "name": name,
      "period": period_seconds,
      "angular_velocity": angular_velocity,
      "speed_kmh": tip_velocity_kmh,
      "ratio": light_speed_ratio,
      "color": color
  }

# 速度表示関数
def format_speed(speed_kmh: float) -> str:
  if speed_kmh >= 1000:
    return f"{speed_kmh:.2e} km/h"
  else:
    return f"{speed_kmh:.2f} km/h"

# 光速表示関数
def format_light_speed_ratio(ratio: float) -> str:
  percentage = ratio * 100
  if percentage >= 0.001:
    return f"{percentage:.4f} %"
  else:
    return f"{percentage:.2e} %"

# 針追加関数
def add_hari():
  global extra_hari_count
  if not haris_data: return

  last_hand_period = haris_data[-1]["period"]
  new_period = last_hand_period / period_divider

  extra_hari_count += 1
  new_name = f"追加針 {extra_hari_count}"

  new_hari_data = calculate_hari_data(
      new_name, new_period, extra_hari_count)
  haris_data.append(new_hari_data)

# 針消す関数
def remove_hari():
  global extra_hari_count
  if len(haris_data) > 1:
    haris_data.pop()
    extra_hari_count -= 1

# 針角度get関数
def get_hari_angle(hari_data):
  current_time = pygame.time.get_ticks() / 1000.0 - start_time
  angle_rad = hari_data["angular_velocity"] * current_time - math.pi / 2
  return angle_rad % (2 * math.pi)

# ボタン関数
def draw_button(screen, rect, text, color, font):
  pygame.draw.rect(screen, color, rect)
  text_surf = font.render(text, True, black)
  text_rect = text_surf.get_rect(center=rect.center)
  screen.blit(text_surf, text_rect)

# メイン関数
def main():
  global haris_data, start_time, scroll_y, extra_hari_count

  pygame.init()
  screen = pygame.display.set_mode((width, height))
  pygame.display.set_caption("超高速時計シミュレーション")
  clock = pygame.time.Clock()

  start_time = pygame.time.get_ticks() / 1000.0
  haris_data.append(calculate_hari_data("秒針 (基本)", 60.0, 0))

  try:
    font_name = "msgothic"
    font_size_small = 20
    font_size_large = 30
    font = pygame.font.SysFont(font_name, font_size_small)
    font_large = pygame.font.SysFont(font_name, font_size_large)
  except Exception:
    font = pygame.font.Font(None, 24)
    font_large = pygame.font.Font(None, 36)

  button_w, button_h = 130, 40
  button_add_rect = pygame.Rect(50, 500, button_w, button_h)
  button_remove_rect = pygame.Rect(200, 500, button_w, button_h)

  running = True
  while running:
    info_height_per_hand = 80
    total_info_height = len(haris_data) * info_height_per_hand + 50
    max_scroll = max(0, total_info_height - panel_height)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

      if event.type == pygame.MOUSEBUTTONDOWN:
        if button_add_rect.collidepoint(event.pos):
          add_hari()
        elif button_remove_rect.collidepoint(event.pos):
          remove_hari()

      if event.type == pygame.MOUSEWHEEL and panel_rect.collidepoint(pygame.mouse.get_pos()):
        scroll_y += event.y * scroll_speed
        scroll_y = max(min(0, scroll_y), -max_scroll)

    screen.fill(white)

    pygame.draw.circle(screen, black, (center_x, center_y), radius, 2)
    pygame.draw.circle(screen, black, (center_x, center_y), 5)

    for i, hari in enumerate(haris_data):
      angle = get_hari_angle(hari)
      hand_length_px = radius * 0.9

      end_x = center_x + int(hand_length_px * math.cos(angle))
      end_y = center_y + int(hand_length_px * math.sin(angle))

      thickness = max(1, 4 - i)

      pygame.draw.line(
          screen, hari["color"], (center_x, center_y), (end_x, end_y), thickness)

    draw_button(screen, button_add_rect, "ボタン A (追加)", green, font)
    draw_button(screen, button_remove_rect, "ボタン B (削除)", red, font)

    screen.set_clip(panel_rect)

    current_y = panel_top + 10 + scroll_y

    title_surf = font_large.render("針の先端速度", True, black)
    screen.blit(title_surf, (panel_left + 20, current_y))

    current_y += 50

    for i, hari in enumerate(haris_data):
      name_surf = font.render(f"{i}. {hari['name']}", True, hari["color"])
      screen.blit(name_surf, (panel_left + 20, current_y))
      current_y += 20

      period_surf = font.render(
          f"  周期: {hari['period']:.6f} 秒", True, black)
      screen.blit(period_surf, (panel_left + 20, current_y))
      current_y += 20

      kmh_str = format_speed(hari["speed_kmh"])
      speed_kmh_surf = font.render(f"  時速 (v): {kmh_str}", True, black)
      screen.blit(speed_kmh_surf, (panel_left + 20, current_y))
      current_y += 20

      ratio_str = format_light_speed_ratio(hari["ratio"])
      ratio_color = light_magenta if hari["ratio"] > 1.0 else blue_default
      ratio_surf = font.render(f"  光速の: {ratio_str}", True, ratio_color)
      screen.blit(ratio_surf, (panel_left + 20, current_y))
      current_y += 30

    screen.set_clip(None)

    pygame.draw.rect(screen, black, panel_rect, 1)

    pygame.display.flip()
    clock.tick(fps)

  pygame.quit()

if __name__ == "__main__":
  main()
