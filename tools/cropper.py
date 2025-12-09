import sys
import os
import pygame

def main():
    if len(sys.argv) < 2:
        print("usage: python tools/cropper.py <image_path> [item_id]")
        print("example: python tools/cropper.py assets/props.png 4  -> saves item4_1.png ...")
        return
    src_path = sys.argv[1]
    item_id = None
    if len(sys.argv) >= 3:
        try:
            item_id = int(sys.argv[2])
        except ValueError:
            print("item_id must be an integer")
            return

    if not os.path.isfile(src_path):
        print("image not found:", src_path)
        return

    pygame.init()
    img = pygame.image.load(src_path).convert_alpha()
    w, h = img.get_width(), img.get_height()
    screen = pygame.display.set_mode((w, h))
    
    prefix_str = f"item{item_id}_" if item_id else "lv"
    pygame.display.set_caption(f"选择区域: 1..6 保存为 {prefix_str}X.png | Esc 退出 | R 重置")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18, bold=True)

    selecting = False
    start = None
    rect = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    rect = None
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    if rect:
                        lv = event.key - pygame.K_0
                        sub = img.subsurface(rect).copy()
                        os.makedirs("assets", exist_ok=True)
                        if item_id:
                            out_name = f"item{item_id}_{lv}.png"
                        else:
                            out_name = f"lv{lv}.png"
                        out_path = os.path.join("assets", out_name)
                        pygame.image.save(sub, out_path)
                        print("saved:", out_path)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selecting = True
                start = event.pos
                rect = pygame.Rect(start, (0, 0))
            elif event.type == pygame.MOUSEMOTION and selecting:
                x, y = event.pos
                sx, sy = start
                rect = pygame.Rect(min(sx, x), min(sy, y), abs(x - sx), abs(y - sy))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                selecting = False

        screen.fill((30, 30, 30))
        screen.blit(img, (0, 0))
        if rect and rect.w > 0 and rect.h > 0:
            overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 50))
            screen.blit(overlay, (rect.x, rect.y))
            pygame.draw.rect(screen, (255, 215, 0), rect, width=2)

        tip = "拖拽选择区域 | 按 1..6 保存为 lv1..lv6 | R 重置 | Esc 退出"
        surf = font.render(tip, True, (255, 255, 255))
        screen.blit(surf, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

