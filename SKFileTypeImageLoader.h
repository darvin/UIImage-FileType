//
//  SKFileTypeImageLoader.h
//  SparkleShare
//
//  Created by Sergey Klimov on 16.11.11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface SKFileTypeImageLoader : NSObject
{
    NSMutableDictionary *images;
    NSString *filenameFormat;
}
@property (retain) NSDictionary* config;

+(UIImage *) imageForMimeType:(NSString *) mimeType size:(unsigned int) size;

@end
