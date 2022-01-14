
# Đề tài nhóm
Web bán hàng online
## Ngôn ngữ lập trình
* [Django - Python](https://https://www.djangoproject.com//)
* HTML/CSS
* Javascript
## Ảnh xem trước của web
Dưới đây là một số ảnh demo của trang web bán hàng này
* Ảnh danh mục
![ảnh danh mục](https://user-images.githubusercontent.com/58498756/149348475-d8eccdb4-fcb5-4d3c-a0e1-73b4ff63ac3f.png)
* Ảnh giỏ hàng
![ảnh giỏ hàng](https://user-images.githubusercontent.com/58498756/149348488-8c5815aa-8a04-4b00-8d1b-f1e2f578d600.png)
* Ảnh index
![ảnh index](https://user-images.githubusercontent.com/58498756/149348497-e51317d7-7432-4ea3-81fd-1267b2ca5f40.png)
* Ảnh sản phẩm
![ảnh sản phẩm](https://user-images.githubusercontent.com/58498756/149348942-9237d7ae-8d63-45aa-8d5c-f286544e0c36.png)
## Các chức năng chính
* Xem sản phẩm theo độ phổ biến, danh mục, xem gần đây
* Hiện chi tiết các thông số SP
* Thêm SP vào giỏ và đặt SP
* Thông báo like SP và đặt hàng, thêm hàng
* Nhận xét và Đánh giá SP
* Lọc SP theo giá và sắp xếp theo độ phổ biến, giá từ thấp đến cao và ngược lại
* Tìm kiếm sản phẩm theo tên và danh mục
* Hiển thị sản phẩm ưu thích, đơn hàng, hoá đơn và đơn đã mua.
### Các phần mềm cần cài trước trong máy
* django
  ```sh
  pip install django
  ```
* django-annoying
    ```sh
  pip install django-annoying
    ```
### Cách sử dụng
1. Clone từ git hub theo đường link
   ```
   git clone https://github.com/leminhdung2701/tiki-shop-main
   ```
2. Chạy chương trình 
   
   Window
   ```
   python manage.py runserver
   ```
   Linux
   ```
   python3 manage.py runserver
   ```
3. Tạo tài khoản admin để truy cập site của admin
     ```
   .\manage.py createsuperuser
   ```

## Thành viên

* Lê Minh Dũng - Nhóm trưởng - leminhdung_t64@hus.edu.vn
* Tăng Thế Duy -  tangtheduy@gmail.com
* Trần Khánh Duy -  email@email_client.com
Project Link: [https://github.com/leminhdung2701/tiki-shop-main](https://github.com/leminhdung2701/tiki-shop-main)

## Chức năng của trang web
* Người dùng có thể mua sản phẩm 
## Database của trang web
![ảnh database](https://user-images.githubusercontent.com/58498756/149351835-6906e74b-2856-42c7-af7b-8ba6bbb42f64.png)
Database của web được thiết kế sơ bộ ở trên [dbdiagram](https://dbdiagram.io/d/61caa6953205b45b73cee09a?fbclid=IwAR17drJ4rWI4cF2o2M7DT3S65VObEHCKuJMrTvHMOovEfuaPjqIym1W5hxg)

Về các model của web thì mọi người có thể đọc ở file [store/models.py](store/models.py)
