from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from pathlib import Path
import util, log


SETTINGS = util.load_json('configuracoes.json')
LOGGER = log.get_logger()
CACHE = util.load_json('cache.json')


def download_slide(driver:WebDriver, path:'Path', name:str, layout:int):
    try:
        if layout == 0:
            el_slide = driver.find_element(By.CSS_SELECTOR, '.Lesson-content a.LessonButton:nth-child(2)')
        else:
            el_slide = driver.find_element(By.CSS_SELECTOR, '.Lesson-content a.LessonButton')
        url = el_slide.get_attribute('href')
        filepath  = path / 'slide'
        name = util.clean_name_file(name) + '.pdf'

        if not util.check_already_file(filepath / name):
            filepath.mkdir(parents=True, exist_ok=True)
            LOGGER.info('---- Baixando slide: ' + name)
            util.download_file(url, filepath / name)
        else:
            LOGGER.info('---- Slide já baixado: ' + name)
    except NoSuchElementException:
        LOGGER.warning('---- Slide não encontrado.')


def download_mentalmap(driver:WebDriver, path:'Path'):
    try:
        el_summary = driver.find_element(By.CSS_SELECTOR, '.Lesson-content a.LessonButton:nth-child(3)')
        url = el_summary.get_attribute('href')
        filepath = path / 'pdf'
        name = 'mapa mental.pdf'

        if not util.check_already_file(filepath / name):
            filepath.mkdir(parents=True, exist_ok=True)
            LOGGER.info('---- Baixando Mapa Mental: ' + name)
            util.download_file(url, filepath / name)
        else:
            LOGGER.info('---- Mapa Mental já baixado: ' + name)
    except NoSuchElementException:
        LOGGER.warning('---- Mapa Mental não encontrado.')


def download_summary(driver:WebDriver, path:'Path'):
    try:
        el_summary = driver.find_element(By.CSS_SELECTOR, '.Lesson-content a.LessonButton')
        url = el_summary.get_attribute('href')
        filepath = path / 'pdf'
        name = 'resumo.pdf'

        if not util.check_already_file(filepath / name):
            filepath.mkdir(parents=True, exist_ok=True)
            LOGGER.info('---- Baixando resumo: ' + name)
            util.download_file(url, filepath / name)
        else:
            LOGGER.info('---- Resumo já baixado: ' + name)
            
    except NoSuchElementException:
        LOGGER.warning('---- Resumo não encontrado.')


def download_pdf(driver:WebDriver, path:'Path', lesson:dict):
    el_ebook = driver.find_element(By.CSS_SELECTOR, '.LessonButtonList a.LessonButton')
    url = el_ebook.get_attribute('href')
    filepath = path / 'pdf'
    name = util.clean_name_file(lesson['name']) + '.pdf'

    if not util.check_already_file(filepath / name):
        LOGGER.info('---- Baixando PDF: ' + name)
        filepath.mkdir(parents=True, exist_ok=True)
        util.download_file(url, filepath / name)
    else:
        LOGGER.info('---- PDF já baixado: ' + name)


def download_video(driver:WebDriver, path:'Path'):
    el_videos = driver.find_elements(By.CSS_SELECTOR, '.ListVideos-items-video .VideoItem')
    for i, el_video in enumerate(el_videos):
        path_video = path / 'videos'
        path_video.mkdir(parents=True, exist_ok=True)
        oname = el_video.find_element(By.CLASS_NAME, 'VideoItem-info-title').get_attribute('textContent')
        name = util.clean_name_file(oname) + '.mp4'

        driver.execute_script("arguments[0].click();", el_video)
        util.sleep(5, 8)

        download_slide(driver, path, oname, i)

        if not util.check_already_file(path_video / name):
            LOGGER.info('---- Baixando video: ' + name)
            url_video = driver.find_element(By.TAG_NAME, 'video').get_attribute('src')
            util.download_file(url_video, path_video / name)
        else:
            LOGGER.info('---- Video já baixado: ' + name)


def download_resources(driver:WebDriver, link:str, path:'Path', lesson:dict):
    driver.get(link)
    util.sleep(10, 15)
    download_pdf(driver, path, lesson)
    download_summary(driver, path)
    download_mentalmap(driver, path)
    download_video(driver, path)


def download_lessons(driver:WebDriver, link:str, course:str, path:'Path'):
    driver.get(link)
    util.sleep(5, 10)
    el_lessons = driver.find_elements(By.CSS_SELECTOR, '.LessonList-item a')
    list_lessons = []
    for el_lesson in el_lessons:
        data = {'link': el_lesson.get_attribute('href')}
        data['name'] = el_lesson.find_element(By.TAG_NAME, 'h2').text
        list_lessons.append(data)
    
    for lesson in list_lessons:
        if lesson['link'] != link:
            path_lesson = path / util.clean_name(lesson['name'])
            path_lesson.mkdir(parents=True, exist_ok=True)
            if not lesson['name'] in CACHE[course]:
                LOGGER.info('-- Baixando Aula: ' + lesson['name'])
                download_resources(driver, lesson['link'], path_lesson, lesson)
                CACHE[course].append(lesson['name'])
            else:
                LOGGER.info('-- Aula já Baixada: ' + lesson['name'])
        else:
            LOGGER.warning('-- Aula indisponível: ' + lesson['name'])
        
        util.save_json('cache.json', CACHE)


def download_courses(driver:WebDriver):
    el_courses = driver.find_elements(By.CSS_SELECTOR, '.sc-uJMKN.jWnyVI > section a')
    list_course = []
    for elem in el_courses:
        data = {'name': elem.find_element(By.TAG_NAME, 'h1').text}
        data['link'] = elem.get_attribute('href')
        if 'aulas' in data['link']:
            list_course.append(data)
    
    for course in list_course:
        if SETTINGS['cursos'] and not course['name'] in SETTINGS['cursos']:
            continue
        if not course['name'] in CACHE:
            CACHE[course['name']] = []
        LOGGER.info('-' * 200)
        LOGGER.info("# Baixando Curso: " + course['name'])
        course_path = util.create_course_path(SETTINGS['root'], course['name'])
        download_lessons(driver, course['link'], course['name'], course_path)


def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('log-level=3')
    #chrome_options.add_experimental_option("detach", True)
    if not SETTINGS['tela']:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()

    driver.get('https://perfil.estrategia.com/login')
    
    # Fazendo o login
    driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(SETTINGS['login'])
    driver.find_element(By.CSS_SELECTOR, 'input[type="password"').send_keys(SETTINGS['senha'])
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    util.sleep(3, 4)

    driver.get('https://www.estrategiaconcursos.com.br/app/dashboard/cursos')
    util.sleep(10, 15)
    download_courses(driver)


if __name__ == '__main__':
    main()