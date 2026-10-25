const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({
 testDir:'./tests/e2e',timeout:45000,fullyParallel:true,workers:2,
 reporter:[['list'],['json',{outputFile:'test-results/playwright.json'}],['html',{outputFolder:'playwright-report',open:'never'}]],
 use:{baseURL:process.env.TEST_BASE_URL||'http://127.0.0.1:4173',trace:'retain-on-failure'},
 webServer:process.env.TEST_BASE_URL?undefined:{command:'python -m http.server 4173 --bind 127.0.0.1 --directory web/dist',url:'http://127.0.0.1:4173',reuseExistingServer:!process.env.CI},
 projects:[
  {name:'chromium-desktop',use:{browserName:'chromium',viewport:{width:1440,height:1000}}},
  {name:'chromium-mobile',use:{browserName:'chromium',viewport:{width:360,height:780},isMobile:true,hasTouch:true}},
  {name:'webkit-desktop',use:{browserName:'webkit',viewport:{width:1440,height:1000}}},
  {name:'webkit-mobile',use:{browserName:'webkit',viewport:{width:360,height:780},isMobile:true,hasTouch:true}},
 ]
});
