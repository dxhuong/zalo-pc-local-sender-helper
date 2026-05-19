# Zalo PC CSV Sender

Bộ script này dùng Zalo PC trên Windows để đọc danh sách `phone,message` từ CSV, tìm từng số điện thoại trong Zalo PC, dán nội dung, rồi gửi tin.

Phù hợp cho việc test hoặc thao tác có kiểm soát trên tài khoản cá nhân. Không nên dùng để spam, nhắn người lạ hàng loạt, hoặc vượt giới hạn nền tảng.

Đây là công cụ không chính thức, không liên kết với Zalo/VNG. Người dùng tự chịu trách nhiệm tuân thủ điều khoản dịch vụ và pháp luật liên quan.

## Cách dùng nhanh với Codex

1. Copy hoặc giải nén toàn bộ thư mục này vào máy Windows.
2. Mở Codex tại thư mục đó.
3. Mở file `CODEX_QUICK_PROMPT.md`, copy prompt trong đó và gửi cho Codex.
4. Sửa file `contacts.csv` theo danh sách thật.
5. Mở Zalo PC, đăng nhập, để cửa sổ Zalo không bị thu nhỏ.
6. Bảo Codex chạy `run_confirm.ps1` hoặc `run_auto_slow.ps1`.

## Cài đặt thủ công

Mở PowerShell trong thư mục này rồi chạy:

```powershell
.\install_windows.ps1
```

Nếu Windows chặn chạy `.ps1`, chạy lệnh này trong đúng cửa sổ PowerShell đó:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Sau đó chạy lại:

```powershell
.\install_windows.ps1
```

## Chuẩn bị danh sách gửi

File chính là:

```text
contacts.csv
```

Nếu chưa có, script cài đặt sẽ tự tạo từ `contacts_template.csv`.

Định dạng:

```csv
phone,message
"0900000001","Chào anh/chị, đây là tin nhắn mẫu."
"0900000002","Chào anh/chị, đây là tin nhắn thứ hai."
```

Số điện thoại có thể có khoảng trắng, script sẽ tự chuẩn hóa về dạng số liền.

## Kiểm tra CSV

```powershell
.\run_check.ps1
```

## Chạy có xác nhận từng tin

```powershell
.\run_confirm.ps1
```

Mỗi tin sẽ hỏi:

```text
s = gửi
k = bỏ qua
q = dừng
```

## Chạy tự động chậm

```powershell
.\run_auto_slow.ps1
```

Mặc định lệnh này:

- Tự gửi, không hỏi từng tin.
- Nghỉ 2-6 giây trước khi bấm gửi.
- Nghỉ 20-45 giây giữa các tin.

## Khi có lỗi

Lỗi được ghi vào:

```text
zalo_sender.log
```

Trong Codex, chỉ cần nhắn:

```text
đọc zalo_sender.log và sửa lỗi
```

## Các file chính

- `zalo_csv_sender.py`: script điều khiển Zalo PC.
- `contacts.csv`: danh sách thật để gửi, có thể tự tạo.
- `contacts_template.csv`: mẫu CSV sạch để chia sẻ.
- `install_windows.ps1`: cài Python và thư viện.
- `run_check.ps1`: kiểm tra CSV.
- `run_confirm.ps1`: chạy có xác nhận từng tin.
- `run_auto_slow.ps1`: chạy tự động chậm.
- `zalo_sender.log`: log lỗi khi chạy.
