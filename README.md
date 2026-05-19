# Zalo PC Local Sender Helper

Công cụ local trên Windows để đọc danh sách `phone,message` từ CSV, tìm từng số điện thoại trong Zalo PC, dán nội dung và gửi tin.

Đây là công cụ không chính thức, không liên kết với Zalo/VNG. Người dùng tự chịu trách nhiệm tuân thủ điều khoản dịch vụ và pháp luật liên quan. Không dùng để spam, nhắn người lạ hàng loạt, quấy rối, scraping, hoặc vượt giới hạn nền tảng.

## Cách Chạy Bằng Codex

Mở Codex trên máy Windows cần cài, rồi gửi prompt này:

```text
Hãy cài và chạy repo GitHub này trên máy Windows:

https://github.com/dxhuong/zalo-pc-local-sender-helper

Yêu cầu:
1. Clone repo về máy.
2. Vào thư mục repo.
3. Chạy .\install_windows.ps1 để cài Python và dependency nếu thiếu.
4. Kiểm tra contacts.csv bằng .\run_check.ps1.
5. Hướng dẫn tôi sửa contacts.csv với cột phone,message.
6. Nhắc tôi mở Zalo PC, đăng nhập, và để cửa sổ Zalo không bị minimize.
7. Khi tôi xác nhận đã mở Zalo, chạy .\run_confirm.ps1 nếu tôi muốn xác nhận từng tin, hoặc .\run_auto_slow.ps1 nếu tôi muốn gửi tự động chậm.
8. Nếu có lỗi, đọc zalo_sender.log và sửa tiếp.
```

Sau khi Codex cài xong, sửa file:

```text
contacts.csv
```

Rồi bảo Codex:

```text
chạy có xác nhận
```

hoặc:

```text
chạy tự động chậm
```

## Dùng Codex Để Tạo CSV Từ Excel

Nếu bạn có file Excel danh sách khách hàng, có thể upload file đó vào Codex và yêu cầu Codex tự cập nhật `contacts.csv`.

File Excel nên có ít nhất:

- Một cột số điện thoại, ví dụ `phone`, `sdt`, `so_dien_thoai`, `mobile`.
- Một cột nội dung tin nhắn, ví dụ `message`, `noi_dung`, `content`.

Nếu Excel chỉ có số điện thoại và tên, có thể yêu cầu Codex tự tạo nội dung cá nhân hóa.

Prompt mẫu:

```text
Tôi vừa upload file Excel danh sách người nhận.

Hãy đọc file Excel đó và cập nhật contacts.csv trong repo này.

Yêu cầu:
1. Tìm cột số điện thoại. Nếu tên cột không rõ, hãy suy luận từ dữ liệu.
2. Tìm cột nội dung tin nhắn. Nếu không có cột nội dung, hãy tạo nội dung cá nhân hóa lịch sự dựa trên tên nếu có.
3. Xuất đúng format CSV: phone,message
4. Chuẩn hóa số điện thoại: bỏ khoảng trắng, dấu chấm, dấu gạch ngang; giữ số 0 đầu nếu có.
5. Bỏ dòng thiếu số điện thoại.
6. Không chạy gửi Zalo thật.
7. Chạy .\run_check.ps1 để kiểm tra contacts.csv.
8. Báo lại tổng số dòng hợp lệ và các dòng bị bỏ qua nếu có.
```

Ví dụ nếu Excel có cột `Tên` và `SĐT`, nhưng chưa có nội dung:

```text
Hãy đọc file Excel tôi upload, dùng cột Tên và SĐT để tạo contacts.csv.

Nội dung tin nhắn:
"Chào {Tên}, đây là tin nhắn test từ hệ thống gửi Zalo tự động. Nếu nhận được tin này, vui lòng phản hồi giúp mình."

Sau khi tạo xong, chạy .\run_check.ps1. Chưa gửi Zalo thật.
```

Sau khi Codex tạo CSV và kiểm tra OK, mới chạy:

```text
chạy có xác nhận
```

hoặc:

```text
chạy tự động chậm
```

## Cách Cài Thủ Công

Mở PowerShell rồi chạy:

```powershell
git clone https://github.com/dxhuong/zalo-pc-local-sender-helper.git
cd zalo-pc-local-sender-helper
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install_windows.ps1
```

## Chuẩn Bị CSV

File chính là:

```text
contacts.csv
```

Định dạng:

```csv
phone,message
"0900000001","Chào anh/chị, đây là tin nhắn mẫu."
"0900000002","Chào anh/chị, đây là tin nhắn thứ hai."
```

Số điện thoại có thể có khoảng trắng, script sẽ tự chuẩn hóa về dạng số liền.

Kiểm tra CSV:

```powershell
.\run_check.ps1
```

## Chạy Có Xác Nhận

Mở Zalo PC, đăng nhập, để cửa sổ Zalo không bị thu nhỏ, rồi chạy:

```powershell
.\run_confirm.ps1
```

Mỗi tin sẽ hỏi:

```text
s = gửi
k = bỏ qua
q = dừng
```

## Chạy Tự Động Chậm

Mở Zalo PC, đăng nhập, để cửa sổ Zalo không bị thu nhỏ, rồi chạy:

```powershell
.\run_auto_slow.ps1
```

Mặc định lệnh này:

- Tự gửi, không hỏi từng tin.
- Nghỉ 2-6 giây trước khi bấm gửi.
- Nghỉ 20-45 giây giữa các tin.

## Khi Có Lỗi

Lỗi được ghi vào:

```text
zalo_sender.log
```

Trong Codex, nhắn:

```text
đọc zalo_sender.log và sửa lỗi
```

## Các File Chính

- `zalo_csv_sender.py`: script điều khiển Zalo PC.
- `contacts.csv`: danh sách thật để gửi.
- `contacts_template.csv`: mẫu CSV sạch.
- `install_windows.ps1`: cài Python và thư viện.
- `run_check.ps1`: kiểm tra CSV.
- `run_confirm.ps1`: chạy có xác nhận từng tin.
- `run_auto_slow.ps1`: chạy tự động chậm.
- `zalo_sender.log`: log lỗi khi chạy.
