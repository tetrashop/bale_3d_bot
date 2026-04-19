
        const { JSDOM } = require('jsdom');
        const { window } = new JSDOM('');
        global.window = window;
        global.document = window.document;
        global.navigator = window.navigator;

        // لود کردن موتور اصلی
        try {
            require('/data/data/com.termux/files/home/tetrashop-projects/projects/2d-to-3d/real-3d-engine.js');
            console.log("LOG: Engine Loaded Successfully");
            // در اینجا باید متد اصلی موتور صدا زده شود
            } catch (e) {
                console.error("LOG: Error loading engine: " + e.message);
                process.exit(1);
                         }
    