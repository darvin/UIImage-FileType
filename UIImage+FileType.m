//
//  UIImage+FileType.m
//  SparkleShare
//
//  Created by Sergey Klimov on 15.11.11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import "UIImage+FileType.h"
#import "SKFileTypeImageLoader.h"
@implementation UIImage (FileType)
+ (UIImage *)imageForMimeType:(NSString *) mimeType size:(unsigned int) size {
    return [SKFileTypeImageLoader imageForMimeType:mimeType size:size];
};
@end
