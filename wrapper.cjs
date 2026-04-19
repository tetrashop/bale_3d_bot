
// Mock DOM for offline use
global.window = global;
global.document = {
    createElement: () => ({style: {}, getContext: () => ({}) }),
    getElementsByTagName: () => [],
    body: {}
};
global.navigator = {userAgent: 'Node'};
global.HTMLElement = class {};

try {
    require('/data/data/com.termux/files/home/tetrashop-projects/projects/2d-to-3d/real-3d-engine.js');
    console.log('OK');
} catch (e) {
    console.error(e.message);
    process.exit(1);
}
