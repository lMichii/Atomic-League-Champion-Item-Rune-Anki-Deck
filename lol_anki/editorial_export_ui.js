/* Proposal inspection and export. All mutations use the existing session API. */
let proposalView=null, workflowBusy=false;
const proposalPanel=document.createElement('section');
proposalPanel.id='proposalPanel'; proposalPanel.style.cssText='margin:20px;padding:20px;border:1px solid #41444a';
proposalPanel.innerHTML='<h2>Proposal review and export</h2><label>Saved proposal <select id="proposalHistory"><option value="">Choose a proposal</option></select></label><button id="openProposal">Inspect selected proposal</button><div id="proposalResult"><p>Create a proposal from ready cards, then inspect its changes here. Applying and building are separate actions.</p></div>';
$('message').after(proposalPanel);

async function refreshWorkflow(){
 const r=await fetch('/api/workflow');const data=await r.json();if(!r.ok)throw Error(data.error);
 const value=proposalView?.id||$('proposalHistory').value;
 $('proposalHistory').innerHTML='<option value="">Choose a proposal</option>'+data.proposals.map(p=>`<option value="${esc(p.id)}">${esc(p.status)} · ${p.changed_ids.length} changed cards · ${esc(p.id.slice(0,8))}</option>`).join('');
 $('proposalHistory').value=value;
}
function updateProposalButtons(){
 const p=proposalView, busy=workflowBusy||requestBusy;
 if($('applyProposal'))$('applyProposal').disabled=busy||!p?.can_apply||!$('proposalConfirm').checked||!$('proposalReviewer').value.trim();
 if($('buildEditorial'))$('buildEditorial').disabled=busy||p?.status!=='applied'||!$('proposalReviewer').value.trim();
 $('openProposal').disabled=busy||!$('proposalHistory').value;
}
function renderProposal(p){
 proposalView=p;
 const report=p.validation;
 let html=`<h3>${p.status==='built'?'Export complete':p.status==='applied'?'Proposal applied':'Inspect proposed changes'}</h3><p>Proposal <code>${esc(p.id)}</code></p><p>Acceptance SHA-256: <code>${esc(p.accept_token)}</code></p>`;
 if(p.cards){
  html+=`<p><strong>${p.before_count} → ${p.after_count} approved cards</strong>. Added: ${p.groups.added.length}; modified: ${p.groups.modified.length}; removed: ${p.groups.removed.length}.</p>`;
  for(const kind of ['added','modified','removed'])html+=`<details ${p.groups[kind].length?'open':''}><summary>${kind[0].toUpperCase()+kind.slice(1)} IDs (${p.groups[kind].length})</summary>${p.groups[kind].length?`<ul>${p.groups[kind].map(id=>`<li><code>${esc(id)}</code></li>`).join('')}</ul>`:'<p>None</p>'}</details>`;
  html+='<h3>Learning-content and media changes</h3>'+p.cards.map(c=>`<details open><summary>${esc(c.champion)} · ${esc(c.level)} · ${esc(c.ability)} (${esc(c.change)})</summary>${c.diffs.length?c.diffs.map(d=>`<div class="claim"><strong>${esc(d.field.replaceAll('_',' '))}</strong>${d.before!==null?`<p class="source-meta">Before</p><pre>${esc(d.before)}</pre>`:''}<p class="source-meta">Proposed</p><pre>${esc(d.after??'(removed)')}</pre></div>`).join(''):'<p>Review metadata changed; learning text is unchanged.</p>'}</details>`).join('');
  html+=`<p><a href="${esc(p.diff_url)}" target="_blank" rel="noopener">Full record diff</a> · <a href="${esc(p.source_diff_url)}" target="_blank" rel="noopener">Source/provenance diff</a></p>`;
  html+=`<h3>Validation: ${report.errors} errors, ${report.warnings} warnings</h3><p>Warnings remain recorded and are not cleared by this proposal.</p><details><summary>Inspect validation findings (${report.findings.length})</summary><ul>${report.findings.map(f=>`<li class="${f.severity==='error'?'warn':''}"><strong>${esc(f.severity)} · ${esc(f.code)}</strong> · <code>${esc(f.id)}</code>: ${esc(f.message)}</li>`).join('')}</ul></details>`;
 }
 if(p.status==='proposed')html+=`<label>Reviewer <input id="proposalReviewer" type="text" required></label><label>Review notes (optional)<textarea id="proposalNotes"></textarea></label><label><input id="proposalConfirm" type="checkbox"> I inspected the card changes, IDs, source differences and validation warnings, and accept this exact proposal.</label><button id="applyProposal" class="primary" disabled>Apply Reviewed Proposal</button>`;
 if(p.status==='applied')html+=`<p class="ok">The reviewed changes were applied by ${esc(p.apply_result.review.reviewer)}. No APKG has been built yet.</p><label>Reviewer <input id="proposalReviewer" type="text" required></label><label>Export notes (optional)<textarea id="proposalNotes"></textarea></label><button id="buildEditorial" class="primary" disabled>Build Editorial APKG</button>`;
 if(p.status==='built'){
  const b=p.build_result;
  html+=`<p class="ok">${b.package.cards} cards · ${b.package.notes} notes · ${b.package.media} media files. Validation: ${b.validation.errors} errors, ${b.validation.warnings} warnings. APKG integrity: ${esc(b.package.sqlite_integrity)}.</p><p>Output: <code>${esc(b.output)}</code></p><p>SHA-256: <code>${esc(b.package.sha256)}</code></p><p><a id="downloadApkg" href="${esc(p.download_url)}" download>Download Editorial APKG</a></p>`;
 }
 $('proposalResult').innerHTML=html;
 if($('proposalReviewer')){
  $('proposalReviewer').value=sessionStorage.getItem('league-reviewer')||'';
  $('proposalReviewer').oninput=()=>{sessionStorage.setItem('league-reviewer',$('proposalReviewer').value);updateProposalButtons()};
 }
 if($('proposalConfirm'))$('proposalConfirm').onchange=updateProposalButtons;
 if($('applyProposal'))$('applyProposal').onclick=()=>workflowAction(async()=>{
  const result=await post({action:'apply-proposal',proposal_id:p.id,accept_token:p.accept_token,inspection_token:p.inspection_token,
   reviewer:$('proposalReviewer').value.trim(),notes:$('proposalNotes').value,confirmed:$('proposalConfirm').checked});
  renderProposal(result.result);await load();await refreshWorkflow();
 });
 if($('buildEditorial'))$('buildEditorial').onclick=()=>workflowAction(async()=>{
  const result=await post({action:'build-editorial',proposal_id:p.id,reviewer:$('proposalReviewer').value.trim(),notes:$('proposalNotes').value});
  renderProposal(result.result);await refreshWorkflow();
 });
 updateProposalButtons();
}
async function inspectProposal(id){
 const response=await fetch('/api/proposal?id='+encodeURIComponent(id));const p=await response.json();
 if(!response.ok)throw Error(p.error);renderProposal(p);proposalPanel.scrollIntoView({block:'start',behavior:'smooth'});
}
async function workflowAction(fn){
 if(workflowBusy||requestBusy)return;
 workflowBusy=true;updateProposalButtons();$('propose').disabled=true;
 $('message').textContent='Processing proposal operation…';
 try{await fn();$('message').textContent='Proposal operation completed.'}
 catch(error){if($('proposalConfirm'))$('proposalConfirm').checked=false;$('message').textContent='Proposal operation did not complete: '+error.message}
 finally{workflowBusy=false;renderList();updateProposalButtons()}
}
$('propose').onclick=()=>workflowAction(async()=>{
 const ids=state.cards.filter(c=>c.champion===$('champion').value&&!c.blockers.length).map(c=>c.id);
 const r=await post({action:'propose',ids});await inspectProposal(r.result.id);await refreshWorkflow();
});
$('openProposal').onclick=()=>workflowAction(()=>inspectProposal($('proposalHistory').value));
$('proposalHistory').onchange=updateProposalButtons;
refreshWorkflow().then(updateProposalButtons).catch(e=>$('message').textContent=e.message);
