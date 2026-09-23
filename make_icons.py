import zlib
import struct
from pathlib import Path

def create_png(width, height, file_path):
    """純粋Python (zlib + struct) で美しいAIグラデーションアイコンPNGを生成"""
    raw_data = bytearray()
    
    # 円の半径
    center_x, center_y = width / 2.0, height / 2.0
    corner_radius = width * 0.22 # 角丸四角形
    
    for y in range(height):
        raw_data.append(0)  # filter type 0 (None)
        # 縦方向のグラデーション比率 (0.0 - 1.0)
        ty = y / float(height - 1)
        
        for x in range(width):
            tx = x / float(width - 1)
            
            # 背景色: 上(#1e1b4b ディープインディゴ) から 下(#3b82f6 ビビッドブルー) へのグラデーション
            r = int(30 * (1 - ty) + 59 * ty)
            g = int(27 * (1 - ty) + 130 * ty)
            b = int(75 * (1 - ty) + 246 * ty)
            
            # 中央付近に光彩エフェクト
            dx = (x - center_x) / (width * 0.35)
            dy = (y - center_y) / (height * 0.35)
            dist_sq = dx * dx + dy * dy
            if dist_sq < 1.0:
                glow = (1.0 - dist_sq) * 0.6
                r = min(255, int(r + 100 * glow))
                g = min(255, int(g + 180 * glow))
                b = min(255, int(b + 255 * glow))
            
            # 「AI」の簡易描画（中央の矩形/ピクセルパターン）
            # A: 左の柱、右の柱、横棒、頂点
            # 座標を正規化 (-1.0 to 1.0)
            nx = (x - center_x) / (width * 0.5)
            ny = (y - center_y) / (height * 0.5)
            
            # 中央の白文字エリア判定
            is_text = False
            
            # 'A' (左側: nx in [-0.55, -0.1])
            if -0.52 <= nx <= -0.1 and -0.45 <= ny <= 0.45:
                # 逆V字形状
                slope = (ny - (-0.45)) / 0.9 # 0 at top, 1 at bottom
                left_edge = -0.31 - slope * 0.18
                right_edge = -0.31 + slope * 0.18
                thick = 0.075
                # 左右の斜線
                if abs(nx - left_edge) < thick or abs(nx - right_edge) < thick:
                    is_text = True
                # Aの横棒
                if 0.05 <= ny <= 0.15 and left_edge <= nx <= right_edge:
                    is_text = True
                    
            # 'I' (右側: nx in [0.15, 0.45])
            if 0.15 <= nx <= 0.45 and -0.45 <= ny <= 0.45:
                # 上下の横棒
                if (ny <= -0.33) or (ny >= 0.33):
                    if 0.18 <= nx <= 0.42:
                        is_text = True
                # 中央の縦棒
                if abs(nx - 0.30) < 0.065:
                    is_text = True
                    
            if is_text:
                r, g, b = 255, 255, 255

            raw_data.extend((r, g, b))

    # PNG ヘッダ & チャンクの組み立て
    def make_chunk(chunk_type, data):
        return struct.pack('>I', len(data)) + chunk_type + data + struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)

    png_header = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw_data), 9)
    
    png_bytes = (
        png_header +
        make_chunk(b'IHDR', ihdr) +
        make_chunk(b'IDAT', idat) +
        make_chunk(b'IEND', b'')
    )
    
    file_path.write_bytes(png_bytes)
    print(f"Generated {file_path} ({width}x{height})")

if __name__ == "__main__":
    icon_dir = Path(__file__).resolve().parent / "public" / "icons"
    create_png(192, 192, icon_dir / "icon-192.png")
    create_png(512, 512, icon_dir / "icon-512.png")
    create_png(180, 180, icon_dir / "apple-touch-icon.png")
