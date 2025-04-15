import {chromium} from 'playwright';   // 크롬 브라우저 제어
import lighthouse from 'lighthouse';     // Lighthouse 측정
import fs from 'fs';                     // 파일 저장

// 로그인 이후 측정할 URL
const TEST_URL = 'https://othetak.com/mypage';

(async () => {
    // 1. 브라우저 실행 (remote debugging 포트 열기)
    const browser = await chromium.launch({
        headless: false, // 브라우저 창 보이도록 (테스트 시 확인용)
        args: ['--remote-debugging-port=9222'] // Lighthouse가 연결할 수 있는 포트
    });

    // 2. 새 세션/페이지 열기
    const context = await browser.newContext();
    const page = await context.newPage();

    // 3. 로그인 페이지 이동
    await page.goto('https://othetak.com/login');

    // 4. 로그인 정보 입력 (❗ 셀렉터 실제 구조에 맞게 수정 필요)
    await page.fill('#username', 'your_id');         // 아이디 입력
    await page.fill('#password', 'your_password');   // 비밀번호 입력
    await page.click('#loginButton');                // 로그인 버튼 클릭

    // 5. 로그인 후 이동 대기
    await page.waitForNavigation();

    // 6. Lighthouse 실행 (로그인 유지된 상태)
    const result = await lighthouse(TEST_URL, {
        port: 9222,
        output: 'html',
        logLevel: 'info'
    });

    // 7. 리포트 저장
    fs.writeFileSync('report.html', result.report);

    // 8. 브라우저 종료
    await browser.close();
})();
