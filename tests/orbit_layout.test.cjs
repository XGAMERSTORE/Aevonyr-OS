// Behavioral tests for panel replacement; real Plasma validation remains separate.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');
const code = fs.readFileSync('iso/overlays/usr/share/aevonyr/orbit-layout.js','utf8');
function scenario(fail, applied=false) {
  const removed=[], created=[], messages=[];
  const old={readConfig:()=>applied?'v1':'',remove:()=>removed.push('old')};
  function Panel() {
    const id=created.length;
    this.widgetIds=[];
    this.addWidget=(name)=>{
      if(fail && name==='org.kde.plasma.systemtray')throw Error('missing widget');
      this.widgetIds.push(name);
      return {writeConfig:()=>{}};
    };
    this.remove=()=>removed.push(id);
    this.writeConfig=()=>{};
    created.push(this);
  }
  const context={panels:()=>[old],Panel,print:s=>messages.push(s)};
  let error;
  try {vm.runInNewContext(code,context);}catch(e){error=e;}
  return {removed,created,messages,error};
}
let result=scenario(false);
assert.deepEqual(result.removed,['old']);
assert.equal(result.created.length,2);
assert.equal(result.messages[0],'AEVONYR_APPLIED');
result=scenario(true);
assert.ok(result.error);
assert.deepEqual(result.removed,[0,1]);
result=scenario(false,true);
assert.equal(result.created.length,0);
assert.equal(result.messages[0],'AEVONYR_ALREADY_APPLIED');
console.log('Panel transaction rollback and idempotence passed.');
