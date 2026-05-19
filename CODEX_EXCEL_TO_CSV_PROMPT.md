# Prompt Codex: tạo contacts.csv từ Excel

Upload file Excel vào Codex, rồi gửi prompt này:

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

Nếu Excel chỉ có tên và số điện thoại, dùng prompt này:

```text
Hãy đọc file Excel tôi upload, dùng cột Tên và SĐT để tạo contacts.csv.

Nội dung tin nhắn:
"Chào {Tên}, đây là tin nhắn test từ hệ thống gửi Zalo tự động. Nếu nhận được tin này, vui lòng phản hồi giúp mình."

Yêu cầu:
1. Thay {Tên} bằng tên từng người.
2. Nếu thiếu tên, dùng "anh/chị".
3. Chuẩn hóa số điện thoại.
4. Chạy .\run_check.ps1 sau khi tạo xong.
5. Chưa gửi Zalo thật.
```
