/**
 * Décodé · Suivi — Google Sheets alimenté automatiquement par l'agent 3.
 * Chaque jour (~16 h 10), l'agent 3 envoie « Agent 3 - JJ/MM/AA - Données de suivi · … » avec 4 CSV.
 * Ce script (dans le Google Sheets, compte studiodecodediffusion@gmail.com) lit le dernier mail,
 * remplit 4 onglets et redessine les graphiques. Aucun mot de passe ni token : il lit seulement ta boîte.
 *
 * Installation (une fois) : Extensions → Apps Script → coller ce fichier → Enregistrer →
 * choisir la fonction « installer » → Exécuter → autoriser.
 */
const ONGLETS = {quotidien: 'Jour par jour', videos: 'Vidéos', historique_videos: 'Évolution par vidéo', stories: 'Stories'};

function installer() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('importer').timeBased().everyHours(2).create();
  importer();
}

function importer() {
  const fils = GmailApp.search('subject:"Données de suivi" has:attachment', 0, 1);
  if (!fils.length) return;
  const msgs = fils[0].getMessages();
  const pj = msgs[msgs.length - 1].getAttachments();
  const ss = SpreadsheetApp.getActive();
  pj.forEach(a => {
    const nom = a.getName().replace(/\.csv$/, '');
    const cle = Object.keys(ONGLETS).find(k => nom.startsWith(k + '_'));
    if (!cle) return;
    const lignes = Utilities.parseCsv(a.getDataAsString('UTF-8'))
      .map((r, i) => i === 0 ? r : r.map(c => (c !== '' && !isNaN(c) && !/^\d{4}-/.test(c)) ? Number(c) : c));
    let sh = ss.getSheetByName(ONGLETS[cle]) || ss.insertSheet(ONGLETS[cle]);
    sh.clear(); sh.getCharts().forEach(c => sh.removeChart(c));
    if (!lignes.length) return;
    sh.getRange(1, 1, lignes.length, lignes[0].length).setValues(lignes);
    sh.getRange(1, 1, 1, lignes[0].length).setFontWeight('bold').setBackground('#111').setFontColor('#fff');
    sh.setFrozenRows(1); sh.autoResizeColumns(1, lignes[0].length);
    graphiques(sh, cle, lignes.length);
  });
  const s1 = ss.getSheetByName('Feuille 1') || ss.getSheetByName('Sheet1');
  if (s1 && ss.getSheets().length > 1 && s1.getLastRow() === 0) ss.deleteSheet(s1);
}

function graphe(sh, type, plages, titre, ligne, col, opts) {
  let b = sh.newChart().setChartType(type).setOption('title', titre).setOption('legend', {position: 'bottom'})
    .setOption('width', 620).setOption('height', 320).setPosition(ligne, col, 0, 0);
  plages.forEach(p => b = b.addRange(sh.getRange(p)));
  Object.entries(opts || {}).forEach(([k, v]) => b = b.setOption(k, v));
  sh.insertChart(b.build());
}

function graphiques(sh, cle, n) {
  const C = Charts.ChartType, x = 14;
  if (cle === 'quotidien') {   // A jour, B abonnés, C gagnés, E vues du jour, F portée, G vues profil, K vues stories
    graphe(sh, C.LINE, [`A1:A${n}`, `B1:B${n}`], 'Abonnés', 2, x, {colors: ['#e5133a']});
    graphe(sh, C.COLUMN, [`A1:A${n}`, `C1:C${n}`], 'Abonnés gagnés par jour', 19, x, {colors: ['#2e7d32']});
    graphe(sh, C.LINE, [`A1:A${n}`, `E1:E${n}`, `K1:K${n}`], 'Vues par jour : vidéos et stories', 36, x, {colors: ['#3d5afe', '#ff8a1f']});
    graphe(sh, C.LINE, [`A1:A${n}`, `F1:F${n}`, `G1:G${n}`], 'Portée du compte et visites du profil', 53, x, {colors: ['#8e5cff', '#00b8d4']});
  } else if (cle === 'videos') {   // B titre, D vues, F likes, H partages, I enregistrements, K taux
    graphe(sh, C.BAR, [`B1:B${n}`, `D1:D${n}`], 'Vues par vidéo', n + 3, 1, {colors: ['#3d5afe'], height: 60 + 40 * n});
    graphe(sh, C.BAR, [`B1:B${n}`, `F1:F${n}`, `H1:H${n}`, `I1:I${n}`], 'Likes, partages, enregistrements', n + 3, 7, {isStacked: true, height: 60 + 40 * n});
    graphe(sh, C.COLUMN, [`B1:B${n}`, `K1:K${n}`], "Taux d'engagement (%)", n + 3 + Math.max(10, n * 2), 1, {colors: ['#ff4f81']});
  } else if (cle === 'stories') {
    graphe(sh, C.COLUMN, [`A1:A${n}`, `B1:B${n}`, `C1:C${n}`], 'Vues et portée des stories', 2, 10, {colors: ['#ff8a1f', '#8e5cff']});
  }
}
