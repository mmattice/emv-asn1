# emv-asn1
ASN.1 syntax generator for EMV Tags

This script generates an asn1ate compatible ASN.1 syntax file for EMV specific tags.

I have had to take some liberties with an extra implicit bit in extended tags so that tags don't collide.

For instance:  81 and 9F01 are both context-specific and tagId 1.  The only differentiating factor is that the 9F01 tag has the extended tag bits on in the first byte, which isn't representable except that it makes the 01 the LS7B of the tagId.  By implicitly adding the 8th bit, the tagId becomes 129.

As far as I can tell, no extended tags should have tagIds < 0x1F, but the EMV specs create them anyway.
