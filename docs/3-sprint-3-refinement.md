# Sprint 3 - A Refined and Complete System


## Sprint Goals

Develop the system until it is fully featured, with a refined UI and it satisfies the requirements. The system will be fully tested at this point.


---

## Final Implementation

The web app is fully implemented with a refined UI:

Landing page
![The landing page](screenshots/UI-landing.gif)

Account registration
![Making an account](screenshots/UI-registration.gif)

Logging in
![Logging in](screenshots/UI-login.gif)

Account Verification
![Admin verifies a user](screenshots/UI-verification.gif)

Making a post
![Admin creates a post with an image and video](screenshots/UI-post.gif)

Making and deleting comments
![User makes and deletes a comment](screenshots/UI-comment.gif)

Deleting a post
![Admin deletes a post](screenshots/UI-delete.gif)

User without adequate tier
![User logs in and does not have a high enough tier to see some posts](screenshots/UI-tier.gif)

---

## User Interface Changes

Just having the text "delete" looks a little bit unrefined, common website conventions would use an icon. During my latest meeting with my client, I asked about whether or not he felt an icon would be better.

> "Well I think having the delete text is fine, but for accessibility and icon would be beneficial as well. Could you put a bin icon next to it?"

![Posts without delete icon](screenshots/UI-post1.png)

I then followed this sentiment and added an svg icon next to the delete text. I will follow this convention through out the site, to keep things accessible for everyone.

![Posts with delete icon](screenshots/UI-post2.png)


---

I also realised that whilst posts had a readable date and time, the comments did not. 

![Comments without readable dates](screenshots/UI-comments1.png)

This would not fit with the rest of the site and it is not very friendly for users to read, so I added a format that is consistent with the rest of the site.

![Comments with readable dates](screenshots/UI-comments2.png)


---


Another piece of feedback I got from my client was:

> "It would be good if it also said the name of the tier next to the tier icon, just so I can easily read it"

![Admin dash with just icons](screenshots/UI-admin1.png)

To resolve this, I used a jinja filter to add the text next to the icon.

![Admin dash with text and icons](screenshots/UI-admin2.png)


---

## Sprint Review

This sprint went very smoothly and quickly. It just consisted of me styling the site and making slight adjustments and tweaks to things. I already knew what the site was supposed to look like because of my figma mockup that I made for my client.

