# Pass50 - LOGO.BIC alignment byte fix

## Problem

After the refactor, `LOGO.BIC` rendered 8 pixels shifted again.

## Cause

The type=0 escape-RLE decoder returned the first 8704 decoded bytes directly.

But the decoded stream actually contains one leading alignment/padding byte before the image payload.

This is the same class of issue already seen in type=3 full-image resources.

## Correct rule

For LOGO.BIC:

    header:
        byte 0 = type 0
        byte 1 = escape marker
        word 2 = height
        byte 4 = widthBytes

    image_size = widthBytes * height * 4

Decode escape-RLE until at least:

    image_size + 1

Then render:

    decoded[1 : 1 + image_size]

## Generalized rule

BIC image payload streams discovered so far have a leading decoded alignment byte:

    type=3 full image:
        PackBits(source_data[5:])[1:]

    type=0 LOGO:
        EscapeRLE(source_data[5:])[1:]

This is not a manual pixel shift. It is a stream alignment rule.

## Result

LOGO.BIC renders at the correct horizontal alignment again.
