//
//  UIImage+FileType.h
//  SparkleShare
//
//  Created by Sergey Klimov on 15.11.11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface UIImage (FileType)
+ (UIImage *)imageForMimeType:(NSString *) mimeType size:(unsigned int) size;
@end
