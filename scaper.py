import requests
from bs4 import BeautifulSoup
import pandas as pd

# Hàm cào dữ liệu từ một trang
def scrape_page(url):
    # Gửi yêu cầu HTTP GET tới trang web
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Lỗi khi truy cập {url}: {response.status_code}")
        return []

    # Sử dụng mã hóa thực tế từ phản hồi
    response.encoding = response.apparent_encoding 
    
    # Phân tích nội dung HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Tìm tất cả các mục doanh nghiệp trên trang
    companies = soup.find_all('div', class_='w-100 h-auto shadow rounded-3 bg-white p-2 mb-3')
    
    # Danh sách để lưu thông tin doanh nghiệp
    data = []
    for company in companies:
        # Tìm tên
        name = company.find('h2', class_='p-1 fs-5 h2 m-0 pt-0 ps-0 text-capitalize')
        name = name.text.strip() if name else "Không có tên"
        
        # Tìm ngành nghề
        nganhfind = company.find('span', class_='nganh_listing_txt fw500')
        nganh = nganhfind.text.strip() if nganhfind else "Không có ngành nghề"
        
        # Tìm địa chỉ
        # Tìm tất cả các thẻ <small> chứa địa chỉ, nhưng loại bỏ những thẻ trong div có lớp 'div_textqc' hoặc thẻ có lớp 'text_qc'
        address_tags = company.find_all('small', recursive=True)

        # Kiểm tra và loại bỏ quảng cáo
        addresses = []
        for tag in address_tags:
            # Kiểm tra xem thẻ <small> có thuộc trong div quảng cáo hay không
            if tag.find_parent('div', class_='div_textqc') is None:
                address_text = tag.get_text(strip=True)
                # Loại bỏ quảng cáo hoặc các thẻ không phải địa chỉ thực sự
                if 'VP' not in address_text and 'quảng cáo' not in address_text:
                    addresses.append(address_text)

        # Lưu kết quả địa chỉ (nếu có)
        resultdirec = {
            "Tất cả Địa chỉ": ", ".join(addresses) if addresses else "Không có địa chỉ"
        }



        
        # Tìm mỗi số điện thoại chính
        #phone_tag = company.find('div', class_='pt-0 pb-2 ps-3 pe-4 listing_dienthoai')
        #phone = phone_tag.find('a').text.strip() if phone_tag and phone_tag.find('a') else "Không có số điện thoại"
        
        # Tìm tất cả các thẻ <a> có href bắt đầu bằng "tel:"
        phone_tags = company.find_all('a', href=lambda x: x and x.startswith('tel:'))

        # Lấy số điện thoại từ mỗi thẻ <a>
        phone_numbers = [tag.text.strip() for tag in phone_tags]

        # Tách riêng hotline (nếu có)
        hotline_tag = company.find('div', class_='pt-0 pb-2 ps-3 pe-4')
        hotline = hotline_tag.find('a').text.strip() if hotline_tag and hotline_tag.find('a') else "Không có hotline"

        # Kết quả cuối cùng
        result = {
            "Tất cả số điện thoại": ", ".join(phone_numbers) if phone_numbers else "Không có số điện thoại",
            "Hotline": hotline
        }

        # Tìm trang web
        website_tag = company.find('a', {'rel': 'nofollow', 'target': '_blank'})
        website = website_tag['href'] if website_tag and 'href' in website_tag.attrs else "Không có trang web"     
        
        # Lưu thông tin vào danh sách
        data.append({
            'Tên Tìm được': name,
            'Ngành': nganh,
            'Địa Chỉ': ", ".join(addresses),
            'Số Điện Thoại': ", ".join(phone_numbers),
            'Website': website,
        })

    return data

# URL của trang đầu tiên
base_url = "https://trangvangvietnam.com/srch/h%C3%B3a_ch%E1%BA%A5t.html?page="

# Cào dữ liệu từ các trang (ví dụ: trang 1 đến 27)
all_data = []
for page in range(1, 10):  # Thay đổi số trang theo ý muốn, ví dụ 4 trang thì nhập số 5
    print(f"Đang cào dữ liệu từ trang {page}...")
    url = base_url + str(page)
    page_data = scrape_page(url)
    all_data.extend(page_data)

# Kiểm tra nếu có dữ liệu thì ghi ra file Excel
if all_data:
    # Tạo DataFrame từ dữ liệu thu thập
    df = pd.DataFrame(all_data)

    # Ghi dữ liệu ra file Excel
    output_file = "hoa_chat_data.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Dữ liệu đã được lưu vào {output_file}")
else:
    print("Không có dữ liệu để lưu.")