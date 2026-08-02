#let data = json("data.json")
#let doc = data.document
#let tokens = data.tokens
#let identity = doc.identity

#set page(
  paper: if doc.page_size == "a4" { "a4" } else { "us-letter" },
  margin: (
    top: tokens.margin_top_in * 1in,
    bottom: tokens.margin_bottom_in * 1in,
    left: tokens.margin_left_in * 1in,
    right: tokens.margin_right_in * 1in,
  ),
)
#set text(
  font: tokens.font_family,
  size: tokens.body_size_pt * 1pt,
  fill: rgb(tokens.body_hex),
  hyphenate: true,
)
#set par(leading: 0.7em * tokens.density_scale, justify: false)
#show link: set text(fill: rgb(tokens.accent_hex))

#let section-heading(label) = {
  v(tokens.section_gap_pt * 1pt)
  text(size: tokens.heading_size_pt * 1pt, weight: "bold", fill: rgb(tokens.accent_hex), label)
  v(2pt)
  line(length: 100%, stroke: 1.2pt + rgb("#d4d4d4"))
  v(-2pt)
}

#let contact-row() = {
  let items = ()
  if identity.email != "" { items.push(link("mailto:" + identity.email)[#identity.email]) }
  if identity.phone != "" { items.push(identity.phone) }
  if identity.location != "" { items.push(identity.location) }
  for l in identity.links {
    if l.kind != "email" { items.push(link(l.href)[#l.display_text]) }
  }
  if items.len() > 0 {
    align(center)[#text(size: 9.5pt, fill: rgb("#444444"), items.join(tokens.contact_separator))]
    v(8pt)
  }
}

#let bullet-list(items) = {
  if items.len() == 0 { return }
  if tokens.bullet_glyph == "" {
    for item in items { par[#text(size: 9.8pt, item)] }
    return
  }
  list(
    marker: tokens.bullet_glyph,
    indent: 14pt,
    body-indent: 6pt,
    spacing: tokens.bullet_leading * 1em,
    ..items.map(item => [#text(size: 9.8pt, item)]),
  )
}

#align(center)[
  #text(size: tokens.name_size_pt * 1pt, weight: "bold", identity.name)
]
#contact-row()

#for section in doc.sections {
  section-heading(section.heading)
  if section.kind == "summary" {
    par[#text(size: 10pt, section.summary_text)]
  } else if section.kind == "skills" {
    if section.skill_groups.len() > 0 {
      for group in section.skill_groups {
        par[#text(weight: "bold", group.label + ": ")#group.items.join(", ")]
      }
    } else if section.flat_skills.len() > 0 {
      par[#section.flat_skills.join(", ")]
    }
  } else if section.kind == "custom" {
    bullet-list(section.custom_lines)
  } else {
    for entry in section.entries {
      if section.kind == "work_experience" {
        grid(
          columns: (1fr, auto),
          text(weight: "bold", size: 10.5pt, entry.primary),
          if entry.date_display != "" { text(size: 9pt, fill: rgb("#555555"), entry.date_display) },
        )
        grid(
          columns: (1fr, auto),
          text(style: "italic", size: 10pt, entry.secondary),
          if entry.location != "" { text(size: 9pt, fill: rgb("#555555"), entry.location) },
        )
        bullet-list(entry.bullets)
      } else if section.kind == "education" {
        grid(
          columns: (1fr, auto),
          text(weight: "bold", entry.primary),
          if entry.date_display != "" { text(size: 9pt, fill: rgb("#555555"), entry.date_display) },
        )
        if entry.secondary != "" { par[#text(style: "italic", entry.secondary)] }
        for line in entry.extra_lines { par[#text(size: 9.8pt, line)] }
      } else if section.kind == "projects" {
        grid(
          columns: (1fr, auto),
          text(weight: "bold", size: 10.5pt, entry.primary),
          if entry.date_display != "" { text(size: 9pt, fill: rgb("#555555"), entry.date_display) },
        )
        if entry.secondary != "" { par[#text(style: "italic", size: 10pt, entry.secondary)] }
        bullet-list(entry.bullets)
        if entry.links.len() > 0 {
          par[#link(entry.links.at(0).href)[#entry.links.at(0).display_text]]
        }
      } else {
        par[#text(weight: "bold", entry.primary)#if entry.secondary != "" [ — #entry.secondary]]
      }
      v(tokens.entry_gap_pt * 1pt)
    }
  }
}
